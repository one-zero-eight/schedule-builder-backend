from pathlib import Path
from typing import Any, TypeVar

import jsonpatch
import yaml
from fastapi import HTTPException, status
from pydantic import BaseModel

from src.config import settings
from src.modules.schedule_config.event_log import (
    ConfigChangeEvent,
    ConfigChangeEventSummary,
    ConfigEventLog,
    ConfigResource,
)
from src.modules.schedule_config.schemas import (
    CoursesConfig,
    InstructorConfig,
    RoomConfig,
    ScheduleConfig,
    SectionsConfig,
    TermConfig,
)
from src.modules.schedule_config.validation import ValidationContext, validate_resource_update

TModel = TypeVar("TModel", bound=BaseModel)


class ScheduleConfigRepository:
    def __init__(self, config_dir: str | Path | None = None) -> None:
        self.config_dir = Path(config_dir or settings.schedule_config_dir)
        self.event_log = ConfigEventLog(self.config_dir / "history")

    def _file_path(self, name: str) -> Path:
        return self.config_dir / f"{name}.yaml"

    def _ensure_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _read_file(self, path: Path) -> Any:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _atomic_write_yaml(self, path: Path, payload: Any) -> None:
        self._ensure_dir()
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(
                payload,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )
        tmp_path.replace(path)

    def _model_dump(self, model: BaseModel) -> dict[str, Any]:
        return model.model_dump(mode="json", by_alias=True, exclude_none=True)

    def _read_old_dump(self, path: Path, model_type: type[TModel]) -> dict[str, Any]:
        if not path.is_file():
            return {}
        return model_type.model_validate(self._read_file(path) or {}).model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )

    def _validation_context(
        self,
        resource: ConfigResource,
        updated: BaseModel,
    ) -> ValidationContext:
        return ValidationContext(
            sections=updated if resource == "sections" else self.get_sections(),
            rooms=updated if resource == "rooms" else self.get_rooms(),
            instructors=updated if resource == "instructors" else self.get_instructors(),
            courses=updated if resource == "courses" else self.get_courses(),
        )

    def _validate_if_match(self, resource: ConfigResource, if_match: int) -> int:
        current_revision = self.event_log.get_revision(resource)
        if if_match != current_revision:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Revision mismatch: expected {current_revision}, got {if_match}",
            )
        return current_revision

    def _save_with_history(
        self,
        resource: ConfigResource,
        path: Path,
        model: BaseModel,
        model_type: type[TModel],
        *,
        saved_by: str,
        if_match: int,
    ) -> tuple[TModel, int]:
        current_revision = self._validate_if_match(resource, if_match)
        old_dump = self._read_old_dump(path, model_type)
        new_dump = self._model_dump(model)
        validated = model_type.model_validate(new_dump)
        if path.is_file():
            old_value = model_type.model_validate(old_dump)
        elif resource == "term":
            old_value = validated
        else:
            old_value = model_type()
        validation_errors = validate_resource_update(
            resource,
            validated,
            old_value,
            self._validation_context(resource, validated),
        )
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"errors": validation_errors},
            )

        if old_dump == new_dump:
            return validated, current_revision

        patch = jsonpatch.make_patch(old_dump, new_dump).patch
        if not patch:
            return validated, current_revision

        event_id = self.event_log.create_event_id()
        new_revision = current_revision + 1
        snapshot = self.event_log.save_snapshot(resource, event_id, new_dump)
        self._atomic_write_yaml(path, new_dump)
        self.event_log.append(
            resource,
            event_id=event_id,
            revision=new_revision,
            saved_by=saved_by,
            patch=patch,
            snapshot=snapshot,
        )
        self.event_log.set_revision(resource, new_revision)
        return validated, new_revision

    def _load_model(self, path: Path, model: type[TModel]) -> TModel:
        if not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule config resource not found: {path.stem}",
            )
        return model.model_validate(self._read_file(path) or {})

    def _load_model_or_default(self, path: Path, model: type[TModel]) -> TModel:
        if not path.is_file():
            return model()
        return model.model_validate(self._read_file(path) or {})

    def get_revision(self, resource: ConfigResource) -> int:
        return self.event_log.get_revision(resource)

    def list_history(self, resource: ConfigResource) -> list[ConfigChangeEventSummary]:
        return self.event_log.list_events(resource)

    def get_history_event(self, resource: ConfigResource, event_id: str) -> ConfigChangeEvent:
        return self.event_log.get_event(resource, event_id)

    def get_term_history_snapshot(self, event_id: str) -> TermConfig:
        return self.event_log.load_snapshot("term", event_id, TermConfig)

    def get_sections_history_snapshot(self, event_id: str) -> SectionsConfig:
        return self.event_log.load_snapshot("sections", event_id, SectionsConfig)

    def get_courses_history_snapshot(self, event_id: str) -> CoursesConfig:
        return self.event_log.load_snapshot("courses", event_id, CoursesConfig)

    def get_rooms_history_snapshot(self, event_id: str) -> RoomConfig:
        return self.event_log.load_snapshot("rooms", event_id, RoomConfig)

    def get_instructors_history_snapshot(self, event_id: str) -> InstructorConfig:
        return self.event_log.load_snapshot("instructors", event_id, InstructorConfig)

    def get_term(self) -> TermConfig:
        return self._load_model(self._file_path("term"), TermConfig)

    def set_term(self, term: TermConfig, *, saved_by: str, if_match: int) -> tuple[TermConfig, int]:
        return self._save_with_history(
            "term", self._file_path("term"), term, TermConfig, saved_by=saved_by, if_match=if_match
        )

    def get_sections(self) -> SectionsConfig:
        return self._load_model_or_default(self._file_path("sections"), SectionsConfig)

    def set_sections(self, config: SectionsConfig, *, saved_by: str, if_match: int) -> tuple[SectionsConfig, int]:
        return self._save_with_history(
            "sections",
            self._file_path("sections"),
            config,
            SectionsConfig,
            saved_by=saved_by,
            if_match=if_match,
        )

    def get_courses(self) -> CoursesConfig:
        return self._load_model_or_default(self._file_path("courses"), CoursesConfig)

    def set_courses(self, config: CoursesConfig, *, saved_by: str, if_match: int) -> tuple[CoursesConfig, int]:
        return self._save_with_history(
            "courses",
            self._file_path("courses"),
            config,
            CoursesConfig,
            saved_by=saved_by,
            if_match=if_match,
        )

    def get_rooms(self) -> RoomConfig:
        return self._load_model_or_default(self._file_path("rooms"), RoomConfig)

    def set_rooms(self, config: RoomConfig, *, saved_by: str, if_match: int) -> tuple[RoomConfig, int]:
        return self._save_with_history(
            "rooms", self._file_path("rooms"), config, RoomConfig, saved_by=saved_by, if_match=if_match
        )

    def get_instructors(self) -> InstructorConfig:
        return self._load_model_or_default(self._file_path("instructors"), InstructorConfig)

    def set_instructors(
        self, config: InstructorConfig, *, saved_by: str, if_match: int
    ) -> tuple[InstructorConfig, int]:
        return self._save_with_history(
            "instructors",
            self._file_path("instructors"),
            config,
            InstructorConfig,
            saved_by=saved_by,
            if_match=if_match,
        )

    def get_assembled(self) -> ScheduleConfig:
        term = self.get_term()
        sections = self.get_sections()
        rooms = self.get_rooms()
        instructors = self.get_instructors()
        courses = self.get_courses()
        return ScheduleConfig(
            term=term,
            rooms=rooms.rooms,
            instructors=instructors.instructors,
            sections=sections.sections,
            students_groups=sections.students_groups,
            courses=courses.courses,
        )


schedule_config_repository = ScheduleConfigRepository()
