from fastapi import HTTPException, status

from src.modules.bookings.client import RoomDTO, booking_client
from src.modules.issues.checker import IssueChecker
from src.modules.issues.instructor_ids import instructor_id_issues_from_schedule_config
from src.modules.issues.meetings import (
    build_group_to_studying_teachers,
    meetings_from_schedule_config,
    unplaced_issues_from_schedule_config,
)
from src.modules.issues.per_week import per_week_issues_from_schedule_config
from src.modules.issues.schemas import CheckParameters, CheckResults, Issue
from src.modules.schedule_config.repository import schedule_config_repository
from src.modules.schedule_config.schemas import RoomConfig, TermConfig


def _merge_room_capacities(config_rooms: RoomConfig, booking_rooms: list[RoomDTO]) -> dict[str, int | None]:
    capacities: dict[str, int | None] = {room.id: room.capacity for room in config_rooms.rooms}
    for room in booking_rooms:
        capacities.setdefault(room.id, room.capacity)
    return capacities


def _require_term() -> TermConfig:
    try:
        return schedule_config_repository.get_term()
    except HTTPException as exc:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule term config is required for issue checks",
            ) from exc
        raise


async def check_schedule_issues(token: str, params: CheckParameters) -> CheckResults:
    term = _require_term()
    sections = schedule_config_repository.get_sections()
    courses = schedule_config_repository.get_courses()
    instructors = schedule_config_repository.get_instructors()
    config_rooms = schedule_config_repository.get_rooms()

    meetings = meetings_from_schedule_config(courses, sections)
    booking_rooms = await booking_client.get_rooms(token)
    room_capacities = _merge_room_capacities(config_rooms, booking_rooms)
    valid_room_ids = set(room_capacities)

    checker = IssueChecker(
        token,
        courses=courses,
        sections=sections,
        term=term,
        room_to_capacity=room_capacities,
        group_to_studying_teachers=build_group_to_studying_teachers(sections, instructors),
        valid_room_ids=valid_room_ids,
    )

    issues: list[Issue] = []
    if params.check_instructor_id:
        issues.extend(instructor_id_issues_from_schedule_config(instructors, courses))
    if params.check_unplaced:
        issues.extend(unplaced_issues_from_schedule_config(courses, sections))
    if params.check_per_week:
        issues.extend(per_week_issues_from_schedule_config(courses, sections))

    issues.extend(
        await checker.get_issues(
            meetings,
            start_date=term.semester.start_date,
            end_date=term.semester.end_date,
            check_room=params.check_room,
            check_teacher=params.check_teacher,
            check_capacity=params.check_capacity,
            check_group=params.check_group,
            check_student=params.check_student,
            check_outlook=params.check_outlook,
            check_unbooked=params.check_unbooked,
        ),
    )
    return CheckResults(issues=issues)
