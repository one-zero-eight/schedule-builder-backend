import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from metrics import calculate_schedule_metrics  # noqa: E402

from src.modules.schedule_config.schemas import (  # noqa: E402
    ComponentSessionSeries,
    CourseConfig,
    CoursesConfig,
    InstructorSlotPreferenceEntry,
    InstructorSlotPreferenceLevel,
    WeeklyPatternSlot,
)
from src.modules.solver.schemas import SolveResult, SolveStats  # noqa: E402
from src.weekday import Weekday  # noqa: E402
from tests.instructor_preference_fixtures import INSTRUCTOR_ID, minimal_config  # noqa: E402


def _result_with_meeting(weekday: Weekday, start: datetime.time) -> SolveResult:
    return SolveResult(
        status="FEASIBLE",
        schedule=CoursesConfig(
            courses=[
                CourseConfig(
                    name="Intro",
                    components=[
                        CourseConfig.Component(
                            tag="lec",
                            sessions=[
                                ComponentSessionSeries(
                                    audience=["B26-TEST-01"],
                                    weekly_pattern=[
                                        WeeklyPatternSlot(
                                            weekday=weekday,
                                            start_time=start,
                                            end_time=datetime.time(start.hour + 1, start.minute),
                                            instructor=INSTRUCTOR_ID,
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ]
        ),
        stats=SolveStats(meetings=1, slots=4),
    )


def test_metrics_reports_banned_and_discouraged_violations() -> None:
    cfg = minimal_config(
        slot_preferences=[
            InstructorSlotPreferenceEntry(
                weekday=Weekday.MONDAY,
                start_time=datetime.time(9, 0),
                level=InstructorSlotPreferenceLevel.BANNED,
            ),
            InstructorSlotPreferenceEntry(
                weekday=Weekday.TUESDAY,
                start_time=datetime.time(9, 0),
                level=InstructorSlotPreferenceLevel.DISCOURAGED,
            ),
        ],
    )

    banned_metrics = calculate_schedule_metrics(
        _result_with_meeting(Weekday.MONDAY, datetime.time(9, 0)),
        cfg,
    )
    assert any("banned" in conflict.lower() for conflict in banned_metrics.hard_conflicts)

    discouraged_metrics = calculate_schedule_metrics(
        _result_with_meeting(Weekday.TUESDAY, datetime.time(9, 0)),
        cfg,
    )
    assert discouraged_metrics.hatred_instructor_preference_violations_count == 1
    assert discouraged_metrics.hatred_instructor_preference_violations_weighted == 1

    clean_metrics = calculate_schedule_metrics(
        _result_with_meeting(Weekday.MONDAY, datetime.time(10, 40)),
        cfg,
    )
    assert clean_metrics.hatred_instructor_preference_violations_count == 0
    assert not any("banned" in conflict.lower() for conflict in clean_metrics.hard_conflicts)
