import datetime

from tests.instructor_preference_fixtures import (
    InstructorSlotPreferenceEntry,
    InstructorSlotPreferenceLevel,
    Weekday,
    first_weekly_slot,
    minimal_config,
    solve,
)


def test_solver_soft_term_avoids_discouraged_when_feasible(tmp_path) -> None:
    cfg = minimal_config(
        slot_preferences=[
            InstructorSlotPreferenceEntry(
                weekday=Weekday.TUESDAY,
                start_time=datetime.time(10, 40),
                level=InstructorSlotPreferenceLevel.DISCOURAGED,
            )
        ],
    )
    result = solve(cfg, tmp_path)
    assert result.status in ("OPTIMAL", "FEASIBLE")
    slot = first_weekly_slot(result)
    assert slot is not None
    assert not (slot.weekday == Weekday.TUESDAY and slot.start_time == datetime.time(10, 40))
