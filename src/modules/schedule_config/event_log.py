import gzip
import json
import uuid
from pathlib import Path
from typing import Any, Literal, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict

from src.utcnow import utcnow

ConfigResource = Literal["term", "sections", "courses", "rooms", "instructors"]

TModel = TypeVar("TModel", bound=BaseModel)


class ResourceMeta(BaseModel):
    revision: int = 0
    "Monotonic revision of the current resource state"


class ConfigChangeEvent(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    id: str
    "Unique event id"
    resource: ConfigResource
    "Updated schedule-config resource"
    revision: int
    "Resource revision after this event"
    saved_at: str
    "UTC timestamp in ISO format"
    saved_by: str
    "Moderator email"
    patch: list[dict[str, Any]]
    "RFC 6902 JSON Patch operations"
    snapshot: str
    "Gzipped snapshot path relative to the resource history directory"


class ConfigChangeEventSummary(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    id: str
    resource: ConfigResource
    revision: int
    saved_at: str
    saved_by: str
    change_count: int
    "Number of JSON Patch operations in this event"


class ConfigEventLog:
    def __init__(self, history_dir: Path) -> None:
        self.history_dir = history_dir

    def _resource_dir(self, resource: ConfigResource) -> Path:
        return self.history_dir / resource

    def _meta_path(self, resource: ConfigResource) -> Path:
        return self._resource_dir(resource) / "meta.json"

    def _events_path(self, resource: ConfigResource) -> Path:
        return self._resource_dir(resource) / "events.jsonl"

    def _snapshots_dir(self, resource: ConfigResource) -> Path:
        return self._resource_dir(resource) / "snapshots"

    def _snapshot_name(self, event_id: str) -> str:
        return f"{event_id}.json.gz"

    def _snapshot_relative_path(self, event_id: str) -> str:
        return f"snapshots/{self._snapshot_name(event_id)}"

    def get_revision(self, resource: ConfigResource) -> int:
        meta_path = self._meta_path(resource)
        if not meta_path.is_file():
            return 0
        return ResourceMeta.model_validate_json(meta_path.read_text(encoding="utf-8")).revision

    def set_revision(self, resource: ConfigResource, revision: int) -> None:
        resource_dir = self._resource_dir(resource)
        resource_dir.mkdir(parents=True, exist_ok=True)
        meta_path = self._meta_path(resource)
        tmp_path = meta_path.with_suffix(".tmp")
        tmp_path.write_text(ResourceMeta(revision=revision).model_dump_json(), encoding="utf-8")
        tmp_path.replace(meta_path)

    def save_snapshot(self, resource: ConfigResource, event_id: str, payload: dict[str, Any]) -> str:
        snapshots_dir = self._snapshots_dir(resource)
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshots_dir / self._snapshot_name(event_id)
        tmp_path = snapshot_path.with_suffix(snapshot_path.suffix + ".tmp")
        with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        tmp_path.replace(snapshot_path)
        return self._snapshot_relative_path(event_id)

    def load_snapshot(self, resource: ConfigResource, event_id: str, model_type: type[TModel]) -> TModel:
        event = self.get_event(resource, event_id)
        snapshot_path = self._resource_dir(resource) / event.snapshot
        if not snapshot_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Snapshot not found",
            )
        with gzip.open(snapshot_path, "rt", encoding="utf-8") as f:
            payload = json.load(f)
        return model_type.model_validate(payload)

    def append(
        self,
        resource: ConfigResource,
        *,
        event_id: str,
        revision: int,
        saved_by: str,
        patch: list[dict[str, Any]],
        snapshot: str,
    ) -> ConfigChangeEvent:
        if not patch:
            raise ValueError("Refusing to append empty patch")

        event = ConfigChangeEvent(
            id=event_id,
            resource=resource,
            revision=revision,
            saved_at=utcnow().isoformat(),
            saved_by=saved_by,
            patch=patch,
            snapshot=snapshot,
        )
        events_path = self._events_path(resource)
        events_path.parent.mkdir(parents=True, exist_ok=True)
        with open(events_path, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json())
            f.write("\n")
        return event

    def list_events(self, resource: ConfigResource) -> list[ConfigChangeEventSummary]:
        events_path = self._events_path(resource)
        if not events_path.is_file():
            return []

        summaries: list[ConfigChangeEventSummary] = []
        with open(events_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                event = ConfigChangeEvent.model_validate_json(line)
                summaries.append(
                    ConfigChangeEventSummary(
                        id=event.id,
                        resource=event.resource,
                        revision=event.revision,
                        saved_at=event.saved_at,
                        saved_by=event.saved_by,
                        change_count=len(event.patch),
                    )
                )
        summaries.reverse()
        return summaries

    def get_event(self, resource: ConfigResource, event_id: str) -> ConfigChangeEvent:
        events_path = self._events_path(resource)
        if not events_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History not found",
            )

        with open(events_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                event = ConfigChangeEvent.model_validate_json(line)
                if event.id == event_id:
                    return event

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History event not found",
        )

    def create_event_id(self) -> str:
        return str(uuid.uuid4())
