import datetime
import pprint
from collections import defaultdict
from enum import Enum, StrEnum

from src.config_schema import TeacherDTO
from src.logging_ import logger
from src.modules.bookings.client import BookingDTO, RoomDTO, booking_client
from src.modules.parsers.schemas import BaseLessonDTO, LessonWithExcelCellsDTO

from .graph import UndirectedGraph


class CollisionTypeEnum(StrEnum):
    ROOM = "room"
    TEACHER = "teacher"
    CAPACITY = "capacity"
    OUTLOOK = "outlook"


class LessonWithCollisionTypeDTO(LessonWithExcelCellsDTO):
    collision_type: CollisionTypeEnum
    "Type of collision"
    outlook_info: BookingDTO | None = None
    "Outlook info"
    room_capacity: int | None = None
    "Capacity of the room"


class Weekdays(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class CollisionChecker:
    WEEKDAYS_MAP = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    def __init__(
        self,
        token: str,
        teachers: list[TeacherDTO] | None = None,
        rooms: list[RoomDTO] | None = None,
        graph: UndirectedGraph | None = None,
    ) -> None:
        self.token = token
        self.teachers = teachers or []
        self.rooms = rooms or []
        self.graph = graph or UndirectedGraph()
        self.group_to_studying_teachers = defaultdict(list)
        for teacher in self.teachers:
            self.group_to_studying_teachers[teacher.group].append(teacher)
        self.room_to_capacity = dict()
        for room in self.rooms:
            self.room_to_capacity[room.id] = room.capacity

    @staticmethod
    def check_times_intersect(
        start_a: datetime.time,
        end_a: datetime.time,
        start_b: datetime.time,
        end_b: datetime.time,
    ) -> bool:
        return not (end_a < start_b or end_b < start_a)

    @staticmethod
    def check_datetimes_intersect(
        start_a: datetime.datetime,
        end_a: datetime.datetime,
        start_b: datetime.datetime,
        end_b: datetime.datetime,
    ) -> bool:
        return not (end_a < start_b or end_b < start_a)

    @staticmethod
    def check_two_timeslots_collisions_by_time(
        slot1: BaseLessonDTO,
        slot2: BaseLessonDTO,
    ) -> bool:
        # если у обоих есть date_on, то есть в какую-то дату
        if slot1.date_on is not None and slot2.date_on is not None:
            if slot1.date_on != slot2.date_on:
                return False
            return CollisionChecker.check_times_intersect(
                slot1.start_time,
                slot1.end_time,
                slot2.start_time,
                slot2.end_time,
            )
        # если у обоих нет date_on, а есть weekday
        if slot1.date_on is None and slot2.date_on is None:
            if slot1.weekday != slot2.weekday:
                return False
            return CollisionChecker.check_times_intersect(
                slot1.start_time,
                slot1.end_time,
                slot2.start_time,
                slot2.end_time,
            )
        # если у одного weekday, у другого date_on
        if slot2.date_on is not None:
            slot1, slot2 = slot2, slot1
        if slot2.date_except is not None and slot1.date_on in slot2.date_except:
            return False
        assert slot1.date_on is not None
        assert slot2.weekday is not None

        if slot1.date_on.weekday() != CollisionChecker.WEEKDAYS_MAP.get(slot2.weekday.lower()):
            return False
        return CollisionChecker.check_times_intersect(
            slot1.start_time, slot1.end_time, slot2.start_time, slot2.end_time
        )

    @staticmethod
    def is_online_slot(slot_or_room: BaseLessonDTO | str) -> bool:
        if isinstance(slot_or_room, str):
            return "ONLINE" in slot_or_room
        return "ONLINE" in slot_or_room.room

    @staticmethod
    def _are_lessons_identical(lesson1: LessonWithExcelCellsDTO, lesson2: LessonWithExcelCellsDTO) -> bool:
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
            and lesson1.group_name == lesson2.group_name
        )

    def get_colliding_timeslots(
        self,
        timeslots: list[LessonWithExcelCellsDTO],
        connected_components: list[list[int]],
        collision_type: CollisionTypeEnum,
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        collisions = []
        for component in connected_components:
            if len(component) == 1:
                continue
            collisions_list = []
            for i in component:
                collisions_list.append(
                    LessonWithCollisionTypeDTO(
                        **timeslots[i].model_dump(),
                        collision_type=collision_type,
                    )
                )
            collisions.append(collisions_list)
        return collisions

    def get_collisions_by_room(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        room_to_slots: dict[str, list[tuple[int, LessonWithExcelCellsDTO]]] = defaultdict(list)
        vertices_number = len(timeslots)
        for i, slot in enumerate(timeslots):
            room_to_slots[slot.room].append((i, slot))
        self.graph.create_graph(vertices_number)
        for room, lessons in room_to_slots.items():
            lessons: list[tuple[int, LessonWithExcelCellsDTO]]
            if self.is_online_slot(room):
                logger.info("No need to check room collision for online")
                continue

            if len(lessons) == 1:
                logger.info(f"Room {room} has only one lesson")
                continue

            for i, (ind1, lesson1) in enumerate(lessons):
                if lesson1.lesson_name == "Elective course on Physical Education":
                    logger.info("Skip Physical Education")
                    continue
                for j in range(i + 1, len(lessons)):
                    ind2, lesson2 = lessons[j]
                    if lesson2.lesson_name == "Elective course on Physical Education":
                        logger.info("Skip Physical Education")
                        continue

                    if self.check_two_timeslots_collisions_by_time(lesson1, lesson2):
                        # Skip identical lessons (same lesson appearing in different Excel cells)
                        if self._are_lessons_identical(lesson1, lesson2):
                            logger.info(f"Skipping identical lessons: {lesson1.lesson_name}")
                            continue
                        self.graph.add_edge(ind1, ind2)
        connected_components = self.graph.get_connected_components()
        collisions = self.get_colliding_timeslots(timeslots, connected_components, CollisionTypeEnum.ROOM)
        logger.info(f"Total collisions: {len(collisions)}: {pprint.pformat(collisions)}")
        return collisions

    def get_collisions_by_teacher(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        teachers_to_timeslots: dict[str, list[tuple[int, LessonWithExcelCellsDTO]]] = defaultdict(list)
        self.graph.create_graph(len(timeslots))
        for i, obj in enumerate(timeslots):
            teachers_to_timeslots[obj.teacher].append((i, obj))
            if isinstance(obj.group_name, str):
                if obj.teacher in self.group_to_studying_teachers[obj.group_name]:
                    teachers_to_timeslots[obj.teacher].append((i, obj))
                continue
            for group_name in obj.group_name:
                if obj.teacher in self.group_to_studying_teachers[group_name]:
                    teachers_to_timeslots[obj.teacher].append((i, obj))
        for teacher in teachers_to_timeslots:  # noqa: PLC0206
            n = len(teachers_to_timeslots[teacher])
            for i in range(n):
                ind1, slot1 = teachers_to_timeslots[teacher][i]
                for j in range(i + 1, n):
                    ind2, slot2 = teachers_to_timeslots[teacher][j]
                    if slot1.weekday != slot2.weekday:
                        continue
                    if self.check_two_timeslots_collisions_by_time(slot1, slot2):
                        self.graph.add_edge(ind1, ind2)
        connected_components = self.graph.get_connected_components()
        return self.get_colliding_timeslots(timeslots, connected_components, CollisionTypeEnum.TEACHER)

    def get_lessons_where_not_enough_place_for_students(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        result = []
        for timeslot in timeslots:
            if self.is_online_slot(timeslot):
                continue
            room = timeslot.room
            capacity = self.room_to_capacity.get(room)
            if not capacity:
                # с учётом того, что все "большие" кабинеты заполнены, будет универсальной заменой
                capacity = 30
            if capacity < timeslot.students_number:
                result.append(
                    [
                        LessonWithCollisionTypeDTO(
                            **timeslot.model_dump(),
                            room_capacity=capacity,
                            collision_type=CollisionTypeEnum.CAPACITY,
                        )
                    ]
                )
        return result

    async def get_outlook_collisions(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        min_needed_time: datetime.datetime = datetime.datetime.max
        max_needed_time: datetime.datetime = datetime.datetime.min
        tz = datetime.timezone(datetime.timedelta(hours=3))
        today = datetime.datetime.now(tz).date()

        for lesson in timeslots:
            start_datetime = datetime.datetime.combine(today, lesson.start_time)
            end_datetime = datetime.datetime.combine(today + datetime.timedelta(days=30), lesson.end_time)
            min_needed_time = min(start_datetime, min_needed_time)
            max_needed_time = max(end_datetime, max_needed_time)

        if not timeslots:
            return []

        try:
            all_bookings = await booking_client.get_all_bookings(
                token=self.token,
                start=min_needed_time,
                end=max_needed_time,
            )
        except Exception as e:
            logger.warning(f"Error while fetching bookings: {e}", exc_info=True)
            return []

        collisions = []

        valid_rooms = {room.id for room in self.rooms}

        for lesson in timeslots:
            if self.is_online_slot(lesson) or lesson.room not in valid_rooms:
                continue

            lesson_weekday = lesson_date = None
            if lesson.weekday is not None:
                lesson_weekday = self.WEEKDAYS_MAP.get(lesson.weekday)
            elif lesson.date_on is not None:
                lesson_date = lesson.date_on
            else:
                continue

            lesson_dates = []

            for day_offset in range(30):  # TODO: Change fixed 30-day window to semester based window
                check_date = today + datetime.timedelta(days=day_offset)
                if check_date.weekday() == lesson_weekday and (
                    lesson.date_except is None or check_date not in lesson.date_except
                ):
                    lesson_dates.append(check_date)
                elif check_date == lesson_date:
                    lesson_dates.append(check_date)

            lesson_collisions = [
                LessonWithCollisionTypeDTO(
                    **lesson.model_dump(),
                    collision_type=CollisionTypeEnum.OUTLOOK,
                )
            ]

            for lesson_date in lesson_dates:
                lesson_start = datetime.datetime.combine(lesson_date, lesson.start_time).replace(tzinfo=tz)
                lesson_end = datetime.datetime.combine(lesson_date, lesson.end_time).replace(tzinfo=tz)

                intersected_bookings = list(
                    filter(
                        lambda booking: booking.room_id == lesson.room
                        and self.check_datetimes_intersect(
                            booking.start_time,
                            booking.end_time,
                            lesson_start,
                            lesson_end,
                        ),
                        all_bookings,
                    )
                )

                for booking in intersected_bookings:
                    if booking.title.lower().strip() == lesson.lesson_name.lower().strip():
                        continue

                    if booking.start_time < lesson_end and booking.end_time > lesson_start:
                        booking_as_lesson = LessonWithCollisionTypeDTO(
                            lesson_name=booking.title,
                            weekday=lesson.weekday,
                            start_time=booking.start_time.time(),
                            end_time=booking.end_time.time(),
                            room=lesson.room,
                            teacher="External Booking",  # Placeholder
                            teacher_email="External Booking",
                            group_name=None,
                            students_number=0,
                            collision_type=CollisionTypeEnum.OUTLOOK,
                            outlook_info=booking,
                            excel_range=lesson.excel_range,
                        )

                    if booking_as_lesson not in lesson_collisions:
                        lesson_collisions.append(booking_as_lesson)

            if len(lesson_collisions) > 1:
                collisions.append(lesson_collisions)

        return collisions

    def _sort_by_weekday_and_end_time(self, collisions: list[LessonWithExcelCellsDTO]) -> tuple:
        first_attr = collisions[0].weekday
        second_attr = collisions[0].end_time
        return (
            Weekdays.__members__.get(first_attr, Weekdays.SUNDAY).value,
            second_attr,
        )

    def _sort_collision_group(self, collision_group: list[LessonWithCollisionTypeDTO]) -> None:
        """Sort collision group: unique lessons first, identical lessons last"""
        unique_lessons = []
        identical_lessons = []

        # Group lessons by uniqueness
        for i, lesson in enumerate(collision_group):
            is_identical_to_others = False
            for j, other_lesson in enumerate(collision_group):
                if i != j and self._are_lessons_identical(lesson, other_lesson):
                    is_identical_to_others = True
                    break

            if is_identical_to_others:
                identical_lessons.append(lesson)
            else:
                unique_lessons.append(lesson)

        # Sort each group by weekday and time
        unique_lessons.sort(key=lambda x: (Weekdays.__members__.get(x.weekday, Weekdays.SUNDAY).value, x.end_time))
        identical_lessons.sort(key=lambda x: (Weekdays.__members__.get(x.weekday, Weekdays.SUNDAY).value, x.end_time))

        # Replace collision_group contents: unique first, identical last
        collision_group.clear()
        collision_group.extend(unique_lessons + identical_lessons)

    def sort_collisions(self, collisions: list[list[LessonWithCollisionTypeDTO]]) -> None:
        # Sort each collision group internally
        for collision_group in collisions:
            self._sort_collision_group(collision_group)

        # Sort collision groups by their first lesson
        collisions.sort(key=self._sort_by_weekday_and_end_time)

    async def get_collisions(
        self,
        timeslots: list[LessonWithExcelCellsDTO],
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        logger.info(f"{len(timeslots)} Timeslots")
        collisions = []

        if check_room_collisions:
            _ = self.get_collisions_by_room(timeslots)
            collisions.extend(_)
        if check_teacher_collisions:
            collisions.extend(self.get_collisions_by_teacher(timeslots))
        if check_space_collisions:
            collisions.extend(self.get_lessons_where_not_enough_place_for_students(timeslots))
        if check_outlook_collisions:
            collisions.extend(await self.get_outlook_collisions(timeslots))
        self.sort_collisions(collisions)
        return collisions
