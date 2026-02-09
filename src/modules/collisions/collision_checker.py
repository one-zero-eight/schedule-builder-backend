import datetime
from collections import defaultdict
from collections.abc import Generator
from enum import Enum

from src.core_courses.config import Target as CoreCourseTarget
from src.custom_pydantic import CustomModel
from src.electives.config import Target as ElectiveTarget
from src.logging_ import logger
from src.modules.bookings.client import BookingDTO, RoomDTO, booking_client
from src.modules.collisions.schemas import (
    CapacityIssue,
    CollisionTypeEnum,
    Issue,
    Lesson,
    OutlookIssue,
    RoomIssue,
    TeacherIssue,
)
from src.modules.options.repository import Teacher, VerySameLessonId
from src.utcnow import utcnow

from .graph import UndirectedGraph


class Weekdays(Enum):
    # Monday is 0, Sunday is 6, like in date.weekday()
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @staticmethod
    def get_weekday(weekday: str) -> int:
        return Weekdays[weekday.upper()].value


class CollisionChecker:
    def __init__(
        self,
        token: str,
        teachers: list[Teacher] | None = None,
        rooms: list[RoomDTO] | None = None,
        very_same_lessons: list[list[VerySameLessonId]] | None = None,
    ) -> None:
        self.token = token
        self.teachers = teachers or []
        self.rooms = rooms or []
        self.very_same_lessons: list[list[VerySameLessonId]] = very_same_lessons or []

        # Map student_group -> teachers who are students in that group
        self.group_to_studying_teachers: dict[str, list[Teacher]] = defaultdict(list)
        for teacher in self.teachers:
            if teacher.student_group:
                self.group_to_studying_teachers[teacher.student_group].append(teacher)
        self.room_to_capacity: dict[str, int | None] = dict()
        for room in self.rooms:
            self.room_to_capacity[room.id] = room.capacity

    @staticmethod
    def check_times_intersect(
        start_a: datetime.time,
        end_a: datetime.time,
        start_b: datetime.time,
        end_b: datetime.time,
    ) -> bool:
        _today = datetime.date.today()
        as_datetime_start_a = datetime.datetime.combine(_today, start_a)
        as_datetime_end_a = datetime.datetime.combine(_today, end_a)
        as_datetime_start_b = datetime.datetime.combine(_today, start_b)
        as_datetime_end_b = datetime.datetime.combine(_today, end_b)
        return CollisionChecker.check_datetimes_intersect(
            as_datetime_start_a,
            as_datetime_end_a,
            as_datetime_start_b,
            as_datetime_end_b,
        )

    @staticmethod
    def check_datetimes_intersect(
        start_a: datetime.datetime,
        end_a: datetime.datetime,
        start_b: datetime.datetime,
        end_b: datetime.datetime,
    ) -> bool:
        if (start_a <= start_b <= end_a) or (start_b <= start_a <= end_b):
            return True
        return False

    @staticmethod
    def check_two_timeslots_collisions_by_time(
        slot1: Lesson,
        slot2: Lesson,
    ) -> bool:
        if slot1.date_on and slot2.date_on:
            same_dates = set(slot1.date_on) & set(slot2.date_on)
            if not same_dates:
                return False
            return CollisionChecker.check_times_intersect(
                slot1.start_time,
                slot1.end_time,
                slot2.start_time,
                slot2.end_time,
            )

        elif not slot1.date_on and not slot2.date_on:
            if slot1.weekday != slot2.weekday:
                return False
            return CollisionChecker.check_times_intersect(
                slot1.start_time,
                slot1.end_time,
                slot2.start_time,
                slot2.end_time,
            )

        if slot2.date_on:
            slot1, slot2 = slot2, slot1
        # ONLY ON: main lesson has date_except, nested has date_on; they don't overlap
        if slot2.date_except and slot1.date_on and set(slot1.date_on) <= set(slot2.date_except):
            return False

        assert slot1.date_on
        assert slot2.weekday

        if not any(date.weekday() == Weekdays.get_weekday(slot2.weekday) for date in slot1.date_on):
            return False

        return CollisionChecker.check_times_intersect(
            slot1.start_time, slot1.end_time, slot2.start_time, slot2.end_time
        )

    @staticmethod
    def _rooms_set(lesson: Lesson) -> set[str]:
        if lesson.room is None:
            return set()
        return set(lesson.room if isinstance(lesson.room, tuple) else [lesson.room])

    @staticmethod
    def _is_same_logical_lesson(lesson1: Lesson, lesson2: Lesson) -> bool:
        """Same subject + same room + same teacher + overlapping time = one lesson (e.g. START AT + TILL split)."""
        if lesson1.lesson_name.strip().lower() != lesson2.lesson_name.strip().lower():
            return False
        if CollisionChecker._rooms_set(lesson1) != CollisionChecker._rooms_set(lesson2):
            return False
        t1 = (lesson1.teacher or "").strip().lower()
        t2 = (lesson2.teacher or "").strip().lower()
        if t1 != t2:
            return False
        return CollisionChecker.check_two_timeslots_collisions_by_time(lesson1, lesson2)

    @staticmethod
    def _lesson_matches_identifier(lesson: Lesson, identifier: VerySameLessonId) -> bool:
        """Check if a Lesson matches a VerySameLessonId identifier."""
        if identifier.type and lesson.source_type and identifier.type != lesson.source_type:
            return False
        if lesson.lesson_name.strip().lower() != identifier.title.strip().lower():
            return False
        if identifier.instructor:
            if not lesson.teacher or lesson.teacher.strip().lower() != identifier.instructor.strip().lower():
                return False
        if identifier.groups:
            lesson_groups: set[str] = set()
            if lesson.group_name:
                if isinstance(lesson.group_name, tuple):
                    lesson_groups = set(lesson.group_name)
                else:
                    lesson_groups = {lesson.group_name}
            if not lesson_groups & set(identifier.groups):
                return False
        return True

    def are_very_same_lessons(self, lesson1: Lesson, lesson2: Lesson) -> bool:
        """Check if two lessons belong to the same very_same_lessons group.
        Should only be called when there is a time segment intersection."""
        for group in self.very_same_lessons:
            matched_ids: set[int] = set()
            for i, identifier in enumerate(group):
                if self._lesson_matches_identifier(lesson1, identifier):
                    matched_ids.add(i)
                if self._lesson_matches_identifier(lesson2, identifier):
                    matched_ids.add(i)
            # Both lessons match different identifiers within the same group
            if len(matched_ids) >= 2:
                id1_match = any(self._lesson_matches_identifier(lesson1, group[i]) for i in matched_ids)
                id2_match = any(self._lesson_matches_identifier(lesson2, group[i]) for i in matched_ids)
                if id1_match and id2_match:
                    return True
        return False

    @staticmethod
    def is_online_slot(lessor_or_room: Lesson | str) -> bool:
        if isinstance(lessor_or_room, str):
            return lessor_or_room.upper() in ("ONLINE", "ОНЛАЙН")
        elif isinstance(lessor_or_room, Lesson):
            if lessor_or_room.room is None:
                return False
            if isinstance(lessor_or_room.room, tuple):
                return all(r.upper() in ("ONLINE", "ОНЛАЙН") for r in lessor_or_room.room)
            return lessor_or_room.room.upper() in ("ONLINE", "ОНЛАЙН")

    @staticmethod
    def _remove_suffix(name: str):
        """Remove suffixes like (lec), (tut) from the end of the string to compare outlook bookings with lessons"""
        name = name.lower().strip()
        for suffix in [
            "доп",
            "перенос",
            "(lec)",
            "(tut)",
            "(lab)",
            "(lec + tut)",
            "(lec + lab)",
            "(лек)",
            "(тут)",
            "(лаб)",
            "(лек + тут)",
            "(лек + лаб)",
        ]:
            name = name.removesuffix(suffix).rstrip()
        return name

    def check_for_room_issue(self, lessons: list[Lesson]) -> list[RoomIssue]:
        room_to_slots: dict[str, list[tuple[int, Lesson]]] = defaultdict(list)

        vertices_number = len(lessons)
        for i, slot in enumerate(lessons):
            if self.is_online_slot(slot) or slot.room is None:
                continue
            for room in slot.room if isinstance(slot.room, tuple) else [slot.room]:
                room_to_slots[room].append((i, slot))

        graph = UndirectedGraph(vertices_number)
        collision_room_map: dict[tuple[int, int], str] = {}

        for room, room_lessons in room_to_slots.items():
            room_lessons: list[tuple[int, Lesson]]
            if self.is_online_slot(room):
                logger.debug("No need to check room collision for online")
                continue

            if len(room_lessons) == 1:
                logger.debug(f"Room {room} has only one lesson")
                continue

            for i, (ind1, lesson1) in enumerate(room_lessons):
                if lesson1.lesson_name == "Elective course on Physical Education":
                    logger.info("Skip Physical Education")
                    continue
                for j in range(i + 1, len(room_lessons)):
                    ind2, lesson2 = room_lessons[j]
                    if lesson2.lesson_name == "Elective course on Physical Education":
                        logger.debug("Skip Physical Education")
                        continue

                    if lesson1 is lesson2:
                        continue

                    if self._is_same_logical_lesson(lesson1, lesson2):
                        continue

                    if self.check_two_timeslots_collisions_by_time(lesson1, lesson2):
                        if self.are_very_same_lessons(lesson1, lesson2):
                            continue
                        graph.add_edge(ind1, ind2)
                        collision_room_map[(min(ind1, ind2), max(ind1, ind2))] = room

        connected_components = graph.get_connected_components()
        collisions = graph.get_colliding_elements(lessons, connected_components)
        room_issues = []

        for collision in collisions:
            # Find all rooms that are involved in this collision
            conflicting_rooms = set()
            for i, lesson1 in enumerate(collision):
                for j, lesson2 in enumerate(collision[i + 1 :], i + 1):
                    lesson1_idx = lessons.index(lesson1)
                    lesson2_idx = lessons.index(lesson2)
                    edge_key = (min(lesson1_idx, lesson2_idx), max(lesson1_idx, lesson2_idx))
                    if edge_key in collision_room_map:
                        conflicting_rooms.add(collision_room_map[edge_key])

            if conflicting_rooms:
                room_issue = RoomIssue(
                    collision_type=CollisionTypeEnum.ROOM,
                    room=tuple(sorted(conflicting_rooms)) if len(conflicting_rooms) > 1 else list(conflicting_rooms)[0],
                    lessons=sorted(collision, key=lambda x: len(x.room) if isinstance(x.room, tuple) else 1),
                )
                room_issues.append(room_issue)
        return room_issues

    def check_for_teacher_issue(self, lessons: list[Lesson]) -> list[TeacherIssue]:
        class TeacherOccupation(CustomModel):
            teaching_lessons: list[Lesson] = []
            studying_lessons: list[Lesson] = []

        occupancies: dict[str, TeacherOccupation] = defaultdict(TeacherOccupation)

        for lesson in lessons:
            if lesson.teacher:
                teacher_key = lesson.teacher.lower().strip()
                occupancies[teacher_key].teaching_lessons.append(lesson)

        for lesson in lessons:
            if lesson.group_name:
                group_names = lesson.group_name if isinstance(lesson.group_name, tuple) else (lesson.group_name,)
                for group_name in group_names:
                    for teacher_obj in self.group_to_studying_teachers.get(group_name, []):
                        teacher_key = teacher_obj.name.lower().strip()
                        occupancies[teacher_key].studying_lessons.append(lesson)

        teacher_issues = []

        for teacher, occupation in occupancies.items():
            occupation_lessons = occupation.teaching_lessons + occupation.studying_lessons

            graph = UndirectedGraph(len(occupation_lessons))
            # find collisions in occupation_lessons
            for i, lesson1 in enumerate(occupation_lessons):
                for j in range(i + 1, len(occupation_lessons)):
                    lesson2 = occupation_lessons[j]
                    if self._is_same_logical_lesson(lesson1, lesson2):
                        continue
                    if self.check_two_timeslots_collisions_by_time(lesson1, lesson2):
                        if self.are_very_same_lessons(lesson1, lesson2):
                            continue
                        graph.add_edge(i, j)

            connected_components = graph.get_connected_components()
            collisions_indices_list = graph.get_colliding_elements(
                list(range(len(occupation_lessons))), connected_components
            )

            for collision_indices in collisions_indices_list:
                teaching_lessons = []
                studying_lessons = []
                for i in collision_indices:
                    if i < len(occupation.teaching_lessons):
                        teaching_lessons.append(occupation.teaching_lessons[i])
                    else:
                        studying_lessons.append(occupation.studying_lessons[i - len(occupation.teaching_lessons)])

                teacher_issue = TeacherIssue(
                    collision_type=CollisionTypeEnum.TEACHER,
                    teacher=teacher,
                    teaching_lessons=teaching_lessons,
                    studying_lessons=studying_lessons,
                )
                teacher_issues.append(teacher_issue)

        return teacher_issues

    def check_for_capacity_issue(self, lessons: list[Lesson]) -> list[CapacityIssue]:
        result = []
        for lesson in lessons:
            if self.is_online_slot(lesson) or lesson.room is None or isinstance(lesson.room, tuple):
                continue
            capacity = self.room_to_capacity.get(lesson.room)
            if capacity is None:
                logger.warning(f"Room {lesson.room} has no capacity")
                continue
            if lesson.students_number is None:
                logger.info(f"Lesson {lesson.lesson_name} has no students number")
                continue

            if capacity < lesson.students_number:
                result.append(
                    CapacityIssue(
                        collision_type=CollisionTypeEnum.CAPACITY,
                        room=lesson.room,
                        room_capacity=capacity,
                        needed_capacity=lesson.students_number,
                        lesson=lesson,
                    )
                )
        return result

    async def check_for_outlook_issue(
        self, lessons: list[Lesson], targets: list[CoreCourseTarget | ElectiveTarget] | None = None
    ) -> list[OutlookIssue]:
        def daterange(start_date: datetime.date, end_date: datetime.date) -> Generator[datetime.date]:
            days = int((end_date - start_date).days)
            for n in range(days):
                yield start_date + datetime.timedelta(n)

        tz = datetime.timezone(datetime.timedelta(hours=3))
        today = datetime.datetime.now(tz).date()

        if not lessons:
            return []

        targets_list = [t for t in (targets or []) if isinstance(t, CoreCourseTarget)]
        targets_by_sheet: dict[str, CoreCourseTarget] = {target.sheet_name: target for target in targets_list}

        if not targets_list:
            min_needed_time = datetime.datetime.combine(today, datetime.time.min)
            max_needed_time = datetime.datetime.combine(today + datetime.timedelta(days=30), datetime.time.max)
        else:
            all_start_dates = [target.start_date for target in targets_list]
            all_end_dates = [target.end_date for target in targets_list]
            min_start_date = min(*all_start_dates, today)
            max_end_date = max(*all_end_dates, today + datetime.timedelta(days=30))
            min_needed_time = datetime.datetime.combine(min_start_date, datetime.time.min)
            max_needed_time = datetime.datetime.combine(max_end_date, datetime.time.max)
        # Limit max_needed_time to 61 days from min_needed_time
        max_needed_time = min(max_needed_time, min_needed_time + datetime.timedelta(days=61))

        try:
            all_bookings = await booking_client.get_all_bookings(
                token=self.token,
                start=min_needed_time,
                end=max_needed_time,
            )
        except Exception as e:
            logger.warning(f"Error while fetching bookings: {e}", exc_info=True)
            return []

        result = []

        valid_rooms = {room.id for room in self.rooms}
        conflict_edges: list[tuple[Lesson, list[BookingDTO]]] = []

        for lesson in lessons:
            if self.is_online_slot(lesson) or lesson.room is None:
                logger.debug(f"Skipping online or no room lesson: {lesson.lesson_name}, room: {lesson.room}")
                continue
            rooms = lesson.room if isinstance(lesson.room, tuple) else (lesson.room,)
            filtered_rooms = []
            for room in rooms:
                if room in valid_rooms:
                    filtered_rooms.append(room)
                else:
                    logger.warning(f"Room {room} is not valid")

            if not filtered_rooms:
                logger.debug(f"No valid rooms for {lesson.lesson_name}")
                continue

            dates_to_check = []
            target = targets_by_sheet.get(lesson.google_sheet_name)
            if target:
                starts = target.start_date
                ends = target.end_date

                for override in target.override:
                    if lesson.group_name in override.groups or lesson.course_name in override.courses:
                        starts = (
                            override.start_date.date()
                            if isinstance(override.start_date, datetime.datetime)
                            else override.start_date
                        )
                        ends = override.end_date
                        break
            else:
                starts = today
                ends = today + datetime.timedelta(days=30)

            if lesson.date_from:
                starts = lesson.date_from

            daterange_generator = daterange(starts, ends)

            for check_date in daterange_generator:
                if lesson.weekday:
                    if check_date.weekday() == Weekdays.get_weekday(lesson.weekday):
                        if lesson.date_except is None or check_date not in lesson.date_except:
                            dates_to_check.append(check_date)
                elif lesson.date_on and check_date in lesson.date_on:
                    dates_to_check.append(check_date)

            for lesson_date in dates_to_check:
                lesson_start = datetime.datetime.combine(lesson_date, lesson.start_time).replace(tzinfo=tz)
                lesson_end = datetime.datetime.combine(lesson_date, lesson.end_time).replace(tzinfo=tz)

                intersected_bookings = list(
                    filter(
                        lambda booking: booking.room_id in filtered_rooms
                        and self.check_datetimes_intersect(
                            booking.start_time,
                            booking.end_time,
                            lesson_start,
                            lesson_end,
                        ),
                        all_bookings,
                    )
                )

                filtered_intersected_bookings = []

                for booking in intersected_bookings:
                    b_title: str = booking.title.lower().strip()
                    if (
                        b_title == lesson.lesson_name.lower().strip()
                        or b_title == "lectures"
                        or b_title == "labs"
                        or b_title == "schedule assistant iu"
                        or self._remove_suffix(b_title) == self._remove_suffix(lesson.lesson_name)
                    ):
                        logger.debug(f"Skipping booking for that lesson: {lesson.lesson_name} and {booking.title}")
                        continue
                    _now = utcnow()
                    if booking.end_time < _now:
                        logger.debug(
                            f"Skipping booking for that lesson: {lesson.lesson_name} and {booking.title} because it's in the past"
                        )
                        continue
                    filtered_intersected_bookings.append(booking)
                if filtered_intersected_bookings:
                    conflict_edges.append((lesson, filtered_intersected_bookings))

        results = defaultdict(
            lambda: OutlookIssue(
                collision_type=CollisionTypeEnum.OUTLOOK,
                outlook_event_title="",
                lessons=[],
                outlook_info=[],
            )
        )

        for lesson, bookings in conflict_edges:
            for booking in bookings:
                normalized_title = booking.title.lower().strip()
                results[normalized_title].outlook_event_title = booking.title.strip()
                results[normalized_title].lessons.append(lesson)
                results[normalized_title].outlook_info.append(booking)

        for result in results.values():
            # deduplicate lessons
            visited_lessons = set()
            to_remove = []
            for lesson in result.lessons:
                if id(lesson) in visited_lessons:
                    to_remove.append(lesson)
                else:
                    visited_lessons.add(id(lesson))
            for lesson in to_remove:
                result.lessons.remove(lesson)
            result.lessons = sorted(result.lessons, key=lambda x: (x.weekday, x.start_time))

            # deduplicate if booking by id(booking)
            visited = set()
            to_remove = []
            for booking in result.outlook_info:
                if id(booking) in visited:
                    to_remove.append(booking)
                else:
                    visited.add(id(booking))
            for booking in to_remove:
                result.outlook_info.remove(booking)

            result.outlook_info = sorted(result.outlook_info, key=lambda x: (x.start_time, x.room_id))

        result = list(results.values())
        return result

    async def get_collisions(
        self,
        lessons: list[Lesson],
        targets: list[CoreCourseTarget | ElectiveTarget] | None = None,
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[Issue]:
        logger.info(f"{len(lessons)} lessons")
        issues: list[Issue] = []

        if check_room_collisions:
            _ = self.check_for_room_issue(lessons)
            logger.info(f"Found {len(_)} room issues")
            issues.extend(_)
        if check_teacher_collisions:
            _ = self.check_for_teacher_issue(lessons)
            logger.info(f"Found {len(_)} teacher issues")
            issues.extend(_)
        if check_space_collisions:
            _ = self.check_for_capacity_issue(lessons)
            logger.info(f"Found {len(_)} capacity issues")
            issues.extend(_)
        if check_outlook_collisions:
            _ = await self.check_for_outlook_issue(lessons, targets=targets or [])
            logger.info(f"Found {len(_)} outlook issues")
            issues.extend(_)

        logger.info(f"Found {len(issues)} issues")
        return issues
