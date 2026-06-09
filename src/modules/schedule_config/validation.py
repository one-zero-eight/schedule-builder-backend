from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.modules.schedule_config.schemas import (
    ComponentSessionSeries,
    CoursesConfig,
    InstructorConfig,
    RoomConfig,
    SectionsConfig,
    SessionOccurrence,
    TermConfig,
    WeeklyPatternSlot,
)

VIRTUAL_ROOM_IDS = frozenset({"online", "Online", "ONLINE"})


@dataclass(frozen=True)
class ValidationContext:
    sections: SectionsConfig
    rooms: RoomConfig
    instructors: InstructorConfig
    courses: CoursesConfig


def find_duplicates(values: Iterable[str]) -> list[str]:
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for value in values:
        if not value:
            continue
        key = value.casefold()
        if key in seen and seen[key] not in duplicates:
            duplicates.append(value)
        seen[key] = value
    return duplicates


def build_selector_map(sections: SectionsConfig) -> dict[str, set[str]]:
    selector_map: dict[str, set[str]] = {}
    for section in sections.sections:
        for program in section.programs:
            program_groups: set[str] = set(program.groups)
            for track in program.tracks:
                if track.groups:
                    groups = set(track.groups)
                    selector_map[f"@{program.code}/{track.name}"] = groups
                    program_groups.update(groups)
            if program_groups:
                selector_map[f"@{program.code}"] = program_groups
    return selector_map


def expand_group_tokens(tokens: list[str], selector_map: dict[str, set[str]]) -> set[str]:
    expanded: set[str] = set()
    for token in tokens:
        if token in selector_map:
            expanded.update(selector_map[token])
        else:
            expanded.add(token)
    return expanded


def collect_student_group_codes(sections: SectionsConfig) -> set[str]:
    return {group.code for group in sections.students_groups}


def collect_instructor_ids(instructors: InstructorConfig) -> set[str]:
    return {instructor.id for instructor in instructors.instructors}


def collect_room_ids(rooms: RoomConfig) -> set[str]:
    return {room.id for room in rooms.rooms}


def _collect_instructor_pool_ids(pool: list[str | list[str]]) -> set[str]:
    ids: set[str] = set()
    for entry in pool:
        if isinstance(entry, list):
            ids.update(entry)
        else:
            ids.add(entry)
    return ids


def _collect_meeting_instructor_ids(instructor: str | list[str] | None) -> set[str]:
    if instructor is None:
        return set()
    if isinstance(instructor, list):
        return set(instructor)
    return {instructor}


def _collect_session_instructor_ids(session: ComponentSessionSeries) -> set[str]:
    ids: set[str] = set()
    if session.occurrences:
        for occurrence in session.occurrences:
            ids.update(_collect_meeting_instructor_ids(occurrence.instructor))
    if session.weekly_pattern:
        for slot in session.weekly_pattern:
            ids.update(_collect_meeting_instructor_ids(slot.instructor))
            if slot.edits:
                for edit in slot.edits:
                    ids.update(_collect_meeting_instructor_ids(edit.instructor))
    return ids


def _collect_session_room_ids(session: ComponentSessionSeries) -> set[str]:
    rooms: set[str] = set()
    if session.occurrences:
        for occurrence in session.occurrences:
            if occurrence.room:
                rooms.add(occurrence.room)
    if session.weekly_pattern:
        for slot in session.weekly_pattern:
            if slot.room:
                rooms.add(slot.room)
            if slot.edits:
                for edit in slot.edits:
                    if edit.room:
                        rooms.add(edit.room)
    return rooms


@dataclass(frozen=True)
class CourseReferences:
    group_tokens: set[str]
    instructor_ids: set[str]
    room_ids: set[str]


def collect_course_references(courses: CoursesConfig) -> CourseReferences:
    group_tokens: set[str] = set()
    instructor_ids: set[str] = set()
    room_ids: set[str] = set()
    for course in courses.courses:
        for component in course.components:
            group_tokens.update(component.student_groups)
            instructor_ids.update(_collect_instructor_pool_ids(component.instructor_pool))
            if component.sessions:
                for session in component.sessions:
                    group_tokens.update(session.audience)
                    instructor_ids.update(_collect_session_instructor_ids(session))
                    room_ids.update(_collect_session_room_ids(session))
    return CourseReferences(
        group_tokens=group_tokens,
        instructor_ids=instructor_ids,
        room_ids=room_ids,
    )


def _is_known_group_token(token: str, group_codes: set[str], selector_map: dict[str, set[str]]) -> bool:
    if token.startswith("@"):
        return token in selector_map
    return token in group_codes


def _is_known_room_id(room_id: str, room_ids: set[str]) -> bool:
    return room_id in room_ids or room_id in VIRTUAL_ROOM_IDS


def _validate_occurrence_times(path: str, occurrence: SessionOccurrence, errors: list[str]) -> None:
    if occurrence.start_time >= occurrence.end_time:
        errors.append(f"{path}: start_time must be before end_time")


def _validate_weekly_slot_times(path: str, slot: WeeklyPatternSlot, errors: list[str]) -> None:
    if slot.start_time >= slot.end_time:
        errors.append(f"{path}: start_time must be before end_time")


def validate_term(term: TermConfig) -> list[str]:
    errors: list[str] = []
    if term.semester.start_date > term.semester.end_date:
        errors.append("term.semester.start_date must be on or before end_date")
    for index, slot in enumerate(term.time_slots):
        if slot.start_time >= slot.end_time:
            errors.append(f"term.time_slots[{index}]: start_time must be before end_time")
    return errors


def validate_rooms(config: RoomConfig, *, courses: CoursesConfig) -> list[str]:
    errors: list[str] = []
    room_ids = [room.id for room in config.rooms]
    errors.extend(f"Duplicate room id: {room_id!r}" for room_id in find_duplicates(room_ids))
    for index, room in enumerate(config.rooms):
        if not room.id.strip():
            errors.append(f"rooms[{index}].id must not be empty")
    return errors


def validate_rooms_update(old: RoomConfig, new: RoomConfig, *, courses: CoursesConfig) -> list[str]:
    errors = validate_rooms(new, courses=courses)
    removed_ids = collect_room_ids(old) - collect_room_ids(new)
    referenced_ids = collect_course_references(courses).room_ids - VIRTUAL_ROOM_IDS
    for room_id in sorted(removed_ids):
        if room_id in referenced_ids:
            errors.append(f"Cannot remove room {room_id!r}: still referenced in courses")
    return errors


def validate_instructors(config: InstructorConfig) -> list[str]:
    errors: list[str] = []
    instructor_ids = [instructor.id for instructor in config.instructors]
    errors.extend(f"Duplicate instructor id: {instructor_id!r}" for instructor_id in find_duplicates(instructor_ids))
    for index, instructor in enumerate(config.instructors):
        if not instructor.id.strip():
            errors.append(f"instructors[{index}].id must not be empty")
    return errors


def validate_instructors_update(
    old: InstructorConfig,
    new: InstructorConfig,
    *,
    courses: CoursesConfig,
) -> list[str]:
    errors = validate_instructors(new)
    removed_ids = collect_instructor_ids(old) - collect_instructor_ids(new)
    referenced_ids = collect_course_references(courses).instructor_ids
    for instructor_id in sorted(removed_ids):
        if instructor_id in referenced_ids:
            errors.append(f"Cannot remove instructor {instructor_id!r}: still referenced in courses")
    return errors


def validate_sections(config: SectionsConfig) -> list[str]:
    errors: list[str] = []
    group_codes = collect_student_group_codes(config)

    section_codes = [section.code for section in config.sections]
    errors.extend(f"Duplicate section code: {code!r}" for code in find_duplicates(section_codes))

    students_group_codes = [group.code for group in config.students_groups]
    errors.extend(f"Duplicate students_groups code: {code!r}" for code in find_duplicates(students_group_codes))

    program_codes: list[str] = []
    for section_index, section in enumerate(config.sections):
        if not section.code.strip():
            errors.append(f"sections[{section_index}].code must not be empty")
        for program_index, program in enumerate(section.programs):
            program_codes.append(program.code)
            if not program.code.strip():
                errors.append(f"sections[{section_index}].programs[{program_index}].code must not be empty")
            track_codes = [track.code for track in program.tracks]
            errors.extend(
                f"Duplicate track code in program {program.code!r}: {code!r}" for code in find_duplicates(track_codes)
            )
            for group_code in program.groups:
                if group_code not in group_codes:
                    errors.append(
                        f"sections[{section_index}].programs[{program_index}].groups references unknown group {group_code!r}",
                    )
            for track_index, track in enumerate(program.tracks):
                for group_code in track.groups:
                    if group_code not in group_codes:
                        errors.append(
                            f"sections[{section_index}].programs[{program_index}].tracks[{track_index}].groups "
                            f"references unknown group {group_code!r}",
                        )
            for applies_to_code in program.applies_to:
                if applies_to_code not in group_codes:
                    errors.append(
                        f"sections[{section_index}].programs[{program_index}].applies_to "
                        f"references unknown group {applies_to_code!r}",
                    )

    errors.extend(f"Duplicate program code: {code!r}" for code in find_duplicates(program_codes))
    return errors


def validate_sections_update(
    old: SectionsConfig,
    new: SectionsConfig,
    *,
    courses: CoursesConfig,
) -> list[str]:
    errors = validate_sections(new)
    removed_codes = collect_student_group_codes(old) - collect_student_group_codes(new)
    referenced_tokens = collect_course_references(courses).group_tokens
    selector_map = build_selector_map(new)
    referenced_group_codes: set[str] = set()
    for token in referenced_tokens:
        referenced_group_codes.update(expand_group_tokens([token], selector_map))
        if not token.startswith("@"):
            referenced_group_codes.add(token)
    for group_code in sorted(removed_codes):
        if group_code in referenced_group_codes:
            errors.append(f"Cannot remove students_groups entry {group_code!r}: still referenced in courses")
    return errors


def validate_courses(config: CoursesConfig, ctx: ValidationContext) -> list[str]:
    errors: list[str] = []
    group_codes = collect_student_group_codes(ctx.sections)
    selector_map = build_selector_map(ctx.sections)
    instructor_ids = collect_instructor_ids(ctx.instructors)
    room_ids = collect_room_ids(ctx.rooms)

    course_names = [course.name for course in config.courses]
    errors.extend(f"Duplicate course name: {name!r}" for name in find_duplicates(course_names))

    for course_index, course in enumerate(config.courses):
        component_count = len(course.components)
        for component_index, component in enumerate(course.components):
            path = f"courses[{course_index}].components[{component_index}]"
            for token in component.student_groups:
                if not _is_known_group_token(token, group_codes, selector_map):
                    errors.append(f"{path}.student_groups references unknown group or selector {token!r}")

            component_groups = expand_group_tokens(component.student_groups, selector_map)

            for pool_id in _collect_instructor_pool_ids(component.instructor_pool):
                if pool_id not in instructor_ids:
                    errors.append(f"{path}.instructor_pool references unknown instructor {pool_id!r}")

            relates_to = component.relates_to
            if relates_to is not None:
                indices = [relates_to] if isinstance(relates_to, int) else relates_to
                for relates_index in indices:
                    if relates_index < 0 or relates_index >= component_count:
                        errors.append(
                            f"{path}.relates_to references invalid component index {relates_index}",
                        )

            if not component.sessions:
                continue

            for session_index, session in enumerate(component.sessions):
                session_path = f"{path}.sessions[{session_index}]"
                session_groups = expand_group_tokens(session.audience, selector_map)
                if session.audience and not session_groups.issubset(component_groups):
                    errors.append(f"{session_path}.audience must be a subset of component student_groups")
                for audience_token in session.audience:
                    if not _is_known_group_token(audience_token, group_codes, selector_map):
                        errors.append(
                            f"{session_path}.audience references unknown group or selector {audience_token!r}",
                        )

                if session.occurrences:
                    for occurrence_index, occurrence in enumerate(session.occurrences):
                        occurrence_path = f"{session_path}.occurrences[{occurrence_index}]"
                        _validate_occurrence_times(occurrence_path, occurrence, errors)
                        if occurrence.room and not _is_known_room_id(occurrence.room, room_ids):
                            errors.append(
                                f"{occurrence_path}.room references unknown room {occurrence.room!r}",
                            )
                        for meeting_instructor_id in _collect_meeting_instructor_ids(occurrence.instructor):
                            if meeting_instructor_id not in instructor_ids:
                                errors.append(
                                    f"{occurrence_path}.instructor references unknown instructor {meeting_instructor_id!r}",
                                )

                if session.weekly_pattern:
                    for slot_index, slot in enumerate(session.weekly_pattern):
                        slot_path = f"{session_path}.weekly_pattern[{slot_index}]"
                        _validate_weekly_slot_times(slot_path, slot, errors)
                        if slot.room and not _is_known_room_id(slot.room, room_ids):
                            errors.append(f"{slot_path}.room references unknown room {slot.room!r}")
                        for meeting_instructor_id in _collect_meeting_instructor_ids(slot.instructor):
                            if meeting_instructor_id not in instructor_ids:
                                errors.append(
                                    f"{slot_path}.instructor references unknown instructor {meeting_instructor_id!r}",
                                )
                        if slot.edits:
                            for edit_index, edit in enumerate(slot.edits):
                                edit_path = f"{slot_path}.edits[{edit_index}]"
                                if edit.room and not _is_known_room_id(edit.room, room_ids):
                                    errors.append(f"{edit_path}.room references unknown room {edit.room!r}")
                                for meeting_instructor_id in _collect_meeting_instructor_ids(edit.instructor):
                                    if meeting_instructor_id not in instructor_ids:
                                        errors.append(
                                            f"{edit_path}.instructor references unknown instructor {meeting_instructor_id!r}",
                                        )

    return errors


def validate_resource_update(
    resource: str,
    new_value: TermConfig | SectionsConfig | CoursesConfig | RoomConfig | InstructorConfig,
    old_value: TermConfig | SectionsConfig | CoursesConfig | RoomConfig | InstructorConfig,
    ctx: ValidationContext,
) -> list[str]:
    if resource == "term":
        assert isinstance(new_value, TermConfig)
        return validate_term(new_value)
    if resource == "rooms":
        assert isinstance(new_value, RoomConfig) and isinstance(old_value, RoomConfig)
        return validate_rooms_update(old_value, new_value, courses=ctx.courses)
    if resource == "instructors":
        assert isinstance(new_value, InstructorConfig) and isinstance(old_value, InstructorConfig)
        return validate_instructors_update(old_value, new_value, courses=ctx.courses)
    if resource == "sections":
        assert isinstance(new_value, SectionsConfig) and isinstance(old_value, SectionsConfig)
        return validate_sections_update(old_value, new_value, courses=ctx.courses)
    if resource == "courses":
        assert isinstance(new_value, CoursesConfig)
        return validate_courses(new_value, ctx)
    return []
