"""Shared fixtures for instructor preference solver tests."""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from solve import solve_schedule  # noqa: E402

from src.modules.schedule_config.schemas import (  # noqa: E402
    CourseConfig,
    InstructorConfig,
    InstructorSlotPreferenceEntry,
    InstructorSlotPreferenceLevel,
    RoomConfig,
    ScheduleConfig,
    StudentsGroups,
    TermConfig,
    TermTimeSlot,
)
from src.modules.solver.schemas import SolveResult  # noqa: E402
from src.weekday import Weekday  # noqa: E402

GROUP_CODE = "B26-TEST-01"
INSTRUCTOR_ID = "alice@innopolis.ru"
ROOM_ID = "101"


def minimal_term(*, days: list[Weekday] | None = None, slots: list[TermTimeSlot] | None = None) -> TermConfig:
    return TermConfig(
        name="Preference test term",
        semester=TermConfig.DateRange(
            start_date=datetime.date(2026, 6, 1),
            end_date=datetime.date(2026, 8, 2),
        ),
        days=days
        or [
            Weekday.MONDAY,
            Weekday.TUESDAY,
        ],
        time_slots=slots
        or [
            TermTimeSlot(start_time=datetime.time(9, 0), end_time=datetime.time(10, 30)),
            TermTimeSlot(start_time=datetime.time(10, 40), end_time=datetime.time(12, 10)),
        ],
    )


def minimal_config(
    *,
    term: TermConfig | None = None,
    slot_preferences: list[InstructorSlotPreferenceEntry] | None = None,
) -> ScheduleConfig:
    return ScheduleConfig(
        term=term or minimal_term(),
        rooms=[
            RoomConfig.Room(id=ROOM_ID, name="Hall", capacity=50),
        ],
        instructors=[
            InstructorConfig.Instructor(
                id=INSTRUCTOR_ID,
                slot_preferences=slot_preferences or [],
            )
        ],
        students_groups=[
            StudentsGroups(
                code=GROUP_CODE,
                kind="core",
                estimated_size=30,
            )
        ],
        courses=[
            CourseConfig(
                name="Intro",
                course_tags=["core_course"],
                components=[
                    CourseConfig.Component(
                        tag="lec",
                        per_week=1,
                        student_groups=[GROUP_CODE],
                        instructor_pool=[INSTRUCTOR_ID],
                    )
                ],
            )
        ],
    )


def first_weekly_slot(result: SolveResult):
    for course in result.schedule.courses:
        for component in course.components:
            for series in component.sessions or []:
                pattern = series.weekly_pattern or []
                if pattern:
                    return pattern[0]
    return None


def solve(cfg: ScheduleConfig, tmp_path: Path, *, time_limit: int = 30) -> SolveResult:
    return solve_schedule(cfg, time_limit=time_limit, show_progress=False, artifacts_dir=tmp_path)


__all__ = [
    "GROUP_CODE",
    "INSTRUCTOR_ID",
    "InstructorSlotPreferenceEntry",
    "InstructorSlotPreferenceLevel",
    "Weekday",
    "first_weekly_slot",
    "minimal_config",
    "minimal_term",
    "solve",
]
