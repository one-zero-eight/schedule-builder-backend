import datetime
from collections import defaultdict
from collections.abc import Generator
from enum import Enum

from src.custom_pydantic import CustomModel
from src.logging_ import logger
from src.modules.bookings.client import BookingDTO, RoomDTO, booking_client
from src.modules.collisions.schemas import (
    CapacityIssue,
    CollisionTypeEnum,
    Issue,
    OutlookIssue,
    RoomIssue,
    TeacherIssue,
)
from src.modules.options.repository import Teacher, options_repository
from src.modules.parsers.schemas import Lesson
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
    ) -> None:
        self.token = token
        self.teachers = teachers or []
        self.rooms = rooms or []

        self.group_to_studying_teachers: dict[str, list[Teacher]] = defaultdict(list)
        for teacher in self.teachers:
            if teacher.alias is not None:
                self.group_to_studying_teachers[teacher.alias].append(teacher)
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
        overlap_timedelta = min(end_a, end_b) - max(start_a, start_b)
        return overlap_timedelta > datetime.timedelta(minutes=1)

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
        if slot2.date_except and slot1.date_on in slot2.date_except:
            return False

        assert slot1.date_on
        assert slot2.weekday

        if not any(date.weekday() == Weekdays.get_weekday(slot2.weekday) for date in slot1.date_on):
            return False

        return CollisionChecker.check_times_intersect(
            slot1.start_time, slot1.end_time, slot2.start_time, slot2.end_time
        )

    @staticmethod
    def is_online_slot(lessor_or_room: Lesson | str) -> bool:
        if isinstance(lessor_or_room, str):
            return "ONLINE" == lessor_or_room or "ОНЛАЙН" == lessor_or_room
        elif isinstance(lessor_or_room, Lesson):
            if lessor_or_room.room is None:
                return False
            else:
                return "ONLINE" == lessor_or_room.room or "ОНЛАЙН" == lessor_or_room.room

    @staticmethod
    def _are_lessons_identical(lesson1: Lesson, lesson2: Lesson) -> bool:
        """Check if two lessons are identical (excluding Excel cell location)"""
        return (
            lesson1.lesson_name == lesson2.lesson_name
            and lesson1.weekday == lesson2.weekday
            and lesson1.start_time == lesson2.start_time
            and lesson1.end_time == lesson2.end_time
            and lesson1.room == lesson2.room
            and lesson1.teacher == lesson2.teacher
            and lesson1.date_on == lesson2.date_on
            and lesson1.date_except == lesson2.date_except
        )

    @staticmethod
    def _remove_suffix(name: str):
        """Remove suffixes like (lec), (tut) from the end of the string to compare outlook bookings with lessons"""
        name = name.lower().strip()
        for suffix in ["(lec)", "(tut)", "(lab)", "(lec + tut)", "(лек)", "(тут)", "(лаб)", "(лек + тут)"]:
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

                    if self.check_two_timeslots_collisions_by_time(lesson1, lesson2):
                        # Skip identical lessons (same lesson appearing in different Excel cells)
                        if self._are_lessons_identical(lesson1, lesson2):
                            logger.debug(f"Skipping identical lessons: {lesson1.lesson_name}")
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
                occupancies[lesson.teacher].teaching_lessons.append(lesson)

        for lesson in lessons:
            if lesson.group_name:
                group_names = lesson.group_name if isinstance(lesson.group_name, tuple) else (lesson.group_name,)

                for group_name in group_names:
                    group_students = self.group_to_studying_teachers.get(group_name, [])
                    if lesson.teacher in group_students:
                        occupancies[lesson.teacher].studying_lessons.append(lesson)

        teacher_issues = []

        for teacher, occupation in occupancies.items():
            occupation_lessons = occupation.teaching_lessons + occupation.studying_lessons

            graph = UndirectedGraph(len(occupation_lessons))
            # find collisions in occupation_lessons
            for i, lesson1 in enumerate(occupation_lessons):
                for j in range(i + 1, len(occupation_lessons)):
                    lesson2 = occupation_lessons[j]
                    if self.check_two_timeslots_collisions_by_time(lesson1, lesson2):
                        if self._are_lessons_identical(lesson1, lesson2):
                            logger.debug(f"Skipping identical lessons: {lesson1.lesson_name}")
                            continue
                        if lesson1 is lesson2:
                            logger.debug(f"Skipping identical lessons (same id): {lesson1.lesson_name}")
                            continue
                        if (
                            lesson1.excel_range
                            and lesson2.excel_range
                            and lesson1.excel_range == lesson2.excel_range
                            and lesson1.excel_sheet_name == lesson2.excel_sheet_name
                        ):
                            logger.debug(f"Skipping identical lessons (same excel range): {lesson1.lesson_name}")
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
            check_capacity = capacity or 30  # Unspecified capacity is 30
            if check_capacity < lesson.students_number:
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

    def daterange(self, start_date: datetime.date, end_date: datetime.date) -> Generator[datetime.date, None, None]:
        days = int((end_date - start_date).days)
        for n in range(days):
            yield start_date + datetime.timedelta(n)

    async def check_for_outlook_issue(self, lessons: list[Lesson]) -> list[OutlookIssue]:
        tz = datetime.timezone(datetime.timedelta(hours=3))
        today = datetime.datetime.now(tz).date()

        if not lessons:
            return []

        semester = options_repository.get_semester()

        if not semester:
            min_needed_time = datetime.datetime.combine(today, datetime.time.min)
            max_needed_time = datetime.datetime.combine(today + datetime.timedelta(days=30), datetime.time.max)
        else:
            min_needed_time = datetime.datetime.combine(min(semester.start_date, today), datetime.time.min)
            max_needed_time = datetime.datetime.combine(
                max(semester.end_date, today + datetime.timedelta(days=30)), datetime.time.max
            )
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
            starts = semester.start_date if semester else today
            ends = semester.end_date if semester else today + datetime.timedelta(days=30)

            for override in semester.override if semester else []:
                if lesson.group_name in override.groups or lesson.course_name in override.courses:
                    starts = override.start_date
                    ends = override.end_date
                    break

            if lesson.date_from:
                starts = lesson.date_from

            daterange = self.daterange(starts, ends)

            for check_date in daterange:
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
            result.lessons = sorted(result.lessons, key=lambda x: (x.weekday, x.start_time, x.room))

            # deduplicate bookings by event_id
            visited_bookings = set()
            to_remove = []
            for booking in result.outlook_info:
                if booking.event_id in visited_bookings:
                    to_remove.append(booking)
                else:
                    visited_bookings.add(booking.event_id)
            for booking in to_remove:
                result.outlook_info.remove(booking)

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

    def merge_identical_lessons(self, lessons: list[Lesson]) -> list[Lesson]:
        graph = UndirectedGraph(len(lessons))
        for i, lesson1 in enumerate(lessons):
            for j in range(i + 1, len(lessons)):
                lesson2 = lessons[j]
                if self._are_lessons_identical(lesson1, lesson2):
                    graph.add_edge(i, j)
        connected_components = graph.get_connected_components()
        result = []
        for component in connected_components:
            component_lessons = [lessons[i] for i in component]
            if len(component_lessons) > 1:
                excel_ranges = [lesson.excel_range or "" for lesson in component_lessons]
                groups = []
                for lesson in component_lessons:
                    groups.extend(lesson.group_name if isinstance(lesson.group_name, tuple) else [lesson.group_name])
                students_number = sum(lesson.students_number for lesson in component_lessons)
                lesson = component_lessons[0].model_copy()
                lesson.excel_range = ";".join(excel_ranges)
                lesson.group_name = tuple(sorted(groups))
                lesson.students_number = students_number
                result.append(lesson)
            else:
                result.append(component_lessons[0])
        return result

    async def get_collisions(
        self,
        lessons: list[Lesson],
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[Issue]:
        logger.info(f"{len(lessons)} lessons")
        lessons = self.merge_identical_lessons(lessons)
        logger.info(f"{len(lessons)} lessons after merging identical lessons")
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
            _ = await self.check_for_outlook_issue(lessons)
            logger.info(f"Found {len(_)} outlook issues")
            issues.extend(_)

        logger.info(f"Found {len(issues)} issues")
        return issues
