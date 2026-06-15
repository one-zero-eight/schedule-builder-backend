import datetime

from tests.instructor_preference_fixtures import (
    InstructorSlotPreferenceEntry,
    InstructorSlotPreferenceLevel,
    Weekday,
    first_weekly_slot,
    minimal_config,
    minimal_term,
    solve,
)


def test_solver_avoids_banned_slot_when_alternative_exists(tmp_path) -> None:
    cfg = minimal_config(
        slot_preferences=[
            InstructorSlotPreferenceEntry(
                weekday=Weekday.MONDAY,
                start_time=datetime.time(9, 0),
                level=InstructorSlotPreferenceLevel.BANNED,
            )
        ],
    )
    result = solve(cfg, tmp_path)
    assert result.status in ("OPTIMAL", "FEASIBLE")
    slot = first_weekly_slot(result)
    assert slot is not None
    assert not (slot.weekday == Weekday.MONDAY and slot.start_time == datetime.time(9, 0))


def test_solver_infeasible_when_only_slot_is_banned(tmp_path) -> None:
    term = minimal_term(
        days=[Weekday.MONDAY],
        slots=[
            minimal_term().time_slots[0],
        ],
    )
    cfg = minimal_config(
        term=term,
        slot_preferences=[
            InstructorSlotPreferenceEntry(
                weekday=Weekday.MONDAY,
                start_time=datetime.time(9, 0),
                level=InstructorSlotPreferenceLevel.BANNED,
            )
        ],
    )
    result = solve(cfg, tmp_path, time_limit=10)
    assert result.status in ("INFEASIBLE", "EMPTY")


def test_solver_prefers_non_discouraged_slot(tmp_path) -> None:
    cfg = minimal_config(
        slot_preferences=[
            InstructorSlotPreferenceEntry(
                weekday=Weekday.MONDAY,
                start_time=datetime.time(9, 0),
                level=InstructorSlotPreferenceLevel.DISCOURAGED,
            )
        ],
    )
    result = solve(cfg, tmp_path)
    assert result.status in ("OPTIMAL", "FEASIBLE")
    slot = first_weekly_slot(result)
    assert slot is not None
    assert not (slot.weekday == Weekday.MONDAY and slot.start_time == datetime.time(9, 0))
