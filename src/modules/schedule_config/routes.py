from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Path, Response, status

from src.api.dependencies import ModeratorDep, VerifyTokenDep, is_moderator_email
from src.modules.schedule_config.event_log import ConfigChangeEvent, ConfigChangeEventSummary, ConfigResource
from src.modules.schedule_config.repository import schedule_config_repository
from src.modules.schedule_config.schemas import (
    CoursesConfig,
    InstructorConfig,
    RoomConfig,
    ScheduleConfig,
    SectionsConfig,
    TermConfig,
)
from src.modules.schedule_config.visibility import filter_scheduled_instructors

router = APIRouter(prefix="/schedule-config", tags=["Schedule config"])

ConfigResourcePath = Annotated[
    ConfigResource,
    Path(description="Schedule config resource name"),
]
IfMatchHeader = Annotated[str, Header(alias="If-Match")]


def _moderator_email(moderator: ModeratorDep) -> str:
    user, _token = moderator
    return user.email


def _parse_if_match(if_match: str) -> int:
    value = if_match.strip()
    if value.startswith("W/"):
        value = value[2:].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="If-Match must be an integer revision",
        ) from exc


def _set_etag(response: Response, revision: int) -> None:
    response.headers["ETag"] = f'"{revision}"'


def _instructors_for_user(user_and_token: VerifyTokenDep) -> InstructorConfig:
    instructors = schedule_config_repository.get_instructors()
    user, _token = user_and_token
    if is_moderator_email(user.email):
        return instructors
    courses = schedule_config_repository.get_courses().courses
    return filter_scheduled_instructors(instructors, courses)


def _assembled_for_user(user_and_token: VerifyTokenDep) -> ScheduleConfig:
    config = schedule_config_repository.get_assembled()
    user, _token = user_and_token
    if is_moderator_email(user.email):
        return config
    filtered = filter_scheduled_instructors(InstructorConfig(instructors=config.instructors), config.courses)
    return config.model_copy(update={"instructors": filtered.instructors})


@router.get("/")
async def get_schedule_config(user_and_token: VerifyTokenDep) -> ScheduleConfig:
    return _assembled_for_user(user_and_token)


@router.get("/{resource}/history")
async def list_resource_history(
    resource: ConfigResourcePath,
    _user_and_token: VerifyTokenDep,
) -> list[ConfigChangeEventSummary]:
    return schedule_config_repository.list_history(resource)


@router.get("/{resource}/history/{event_id}")
async def get_resource_history_event(
    resource: ConfigResourcePath,
    event_id: str,
    _user_and_token: VerifyTokenDep,
) -> ConfigChangeEvent:
    return schedule_config_repository.get_history_event(resource, event_id)


@router.get("/term")
async def get_term_config(response: Response, _user_and_token: VerifyTokenDep) -> TermConfig:
    config = schedule_config_repository.get_term()
    _set_etag(response, schedule_config_repository.get_revision("term"))
    return config


@router.put("/term")
async def put_term_config(
    response: Response,
    moderator: ModeratorDep,
    term: TermConfig,
    if_match: IfMatchHeader,
) -> TermConfig:
    config, revision = schedule_config_repository.set_term(
        term,
        saved_by=_moderator_email(moderator),
        if_match=_parse_if_match(if_match),
    )
    _set_etag(response, revision)
    return config


@router.get("/term/history/{event_id}/snapshot")
async def get_term_history_snapshot(event_id: str, _user_and_token: VerifyTokenDep) -> TermConfig:
    return schedule_config_repository.get_term_history_snapshot(event_id)


@router.get("/sections")
async def get_sections_config(response: Response, _user_and_token: VerifyTokenDep) -> SectionsConfig:
    config = schedule_config_repository.get_sections()
    _set_etag(response, schedule_config_repository.get_revision("sections"))
    return config


@router.put("/sections")
async def put_sections_config(
    response: Response,
    moderator: ModeratorDep,
    config: SectionsConfig,
    if_match: IfMatchHeader,
) -> SectionsConfig:
    saved_config, revision = schedule_config_repository.set_sections(
        config,
        saved_by=_moderator_email(moderator),
        if_match=_parse_if_match(if_match),
    )
    _set_etag(response, revision)
    return saved_config


@router.get("/sections/history/{event_id}/snapshot")
async def get_sections_history_snapshot(event_id: str, _user_and_token: VerifyTokenDep) -> SectionsConfig:
    return schedule_config_repository.get_sections_history_snapshot(event_id)


@router.get("/courses")
async def get_courses_config(response: Response, _user_and_token: VerifyTokenDep) -> CoursesConfig:
    config = schedule_config_repository.get_courses()
    _set_etag(response, schedule_config_repository.get_revision("courses"))
    return config


@router.put("/courses")
async def put_courses_config(
    response: Response,
    moderator: ModeratorDep,
    config: CoursesConfig,
    if_match: IfMatchHeader,
) -> CoursesConfig:
    saved_config, revision = schedule_config_repository.set_courses(
        config,
        saved_by=_moderator_email(moderator),
        if_match=_parse_if_match(if_match),
    )
    _set_etag(response, revision)
    return saved_config


@router.get("/courses/history/{event_id}/snapshot")
async def get_courses_history_snapshot(event_id: str, _user_and_token: VerifyTokenDep) -> CoursesConfig:
    return schedule_config_repository.get_courses_history_snapshot(event_id)


@router.get("/rooms")
async def get_rooms_config(response: Response, _user_and_token: VerifyTokenDep) -> RoomConfig:
    config = schedule_config_repository.get_rooms()
    _set_etag(response, schedule_config_repository.get_revision("rooms"))
    return config


@router.put("/rooms")
async def put_rooms_config(
    response: Response,
    moderator: ModeratorDep,
    config: RoomConfig,
    if_match: IfMatchHeader,
) -> RoomConfig:
    saved_config, revision = schedule_config_repository.set_rooms(
        config,
        saved_by=_moderator_email(moderator),
        if_match=_parse_if_match(if_match),
    )
    _set_etag(response, revision)
    return saved_config


@router.get("/rooms/history/{event_id}/snapshot")
async def get_rooms_history_snapshot(event_id: str, _user_and_token: VerifyTokenDep) -> RoomConfig:
    return schedule_config_repository.get_rooms_history_snapshot(event_id)


@router.get("/instructors")
async def get_instructors_config(response: Response, user_and_token: VerifyTokenDep) -> InstructorConfig:
    config = _instructors_for_user(user_and_token)
    _set_etag(response, schedule_config_repository.get_revision("instructors"))
    return config


@router.put("/instructors")
async def put_instructors_config(
    response: Response,
    moderator: ModeratorDep,
    config: InstructorConfig,
    if_match: IfMatchHeader,
) -> InstructorConfig:
    saved_config, revision = schedule_config_repository.set_instructors(
        config,
        saved_by=_moderator_email(moderator),
        if_match=_parse_if_match(if_match),
    )
    _set_etag(response, revision)
    return saved_config


@router.get("/instructors/history/{event_id}/snapshot")
async def get_instructors_history_snapshot(event_id: str, user_and_token: VerifyTokenDep) -> InstructorConfig:
    snapshot = schedule_config_repository.get_instructors_history_snapshot(event_id)
    user, _token = user_and_token
    if is_moderator_email(user.email):
        return snapshot
    courses = schedule_config_repository.get_courses().courses
    return filter_scheduled_instructors(snapshot, courses)
