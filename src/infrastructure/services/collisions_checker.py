import datetime
import pprint
from collections import defaultdict

import pytz

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.lesson import (
    BaseLessonDTO,
    LessonWithCollisionTypeDTO,
    LessonWithExcelCellsDTO,
)
from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.enums import CollisionTypeEnum, Weekdays
from src.domain.interfaces.graph import IGraph
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)
from src.logging_ import logger


class CollisionsChecker(ICollisionsChecker):
    def __init__(
        self,
        teachers: list[TeacherDTO],
        rooms: list[RoomDTO],
        booking_service: IBookingService,
        graph: IGraph,
    ) -> None:
        self.teachers = teachers
        self.rooms = rooms
        self.booking_service = booking_service
        self.group_to_studying_teachers = defaultdict(list)
        for teacher in teachers:
            self.group_to_studying_teachers[teacher.group].append(teacher)
        self.room_to_capacity = dict()
        for room in rooms:
            self.room_to_capacity[room.id] = room.capacity
        self.graph = graph

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
        if (slot1.end_time < slot2.start_time) or (
            slot1.start_time > slot2.end_time
        ):
            return False
        return True

    @staticmethod
    def is_online_slot(slot_or_room: BaseLessonDTO | str) -> bool:
        if isinstance(slot_or_room, str):
            return "ONLINE" == slot_or_room
        return "ONLINE" == slot_or_room.room

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
        weekday_to_room_to_slots: dict[
            str, dict[str, list[tuple[int, LessonWithExcelCellsDTO]]]
        ] = defaultdict(lambda: defaultdict(list))
        vertices_number = len(timeslots)
        for i, slot in enumerate(timeslots):
            weekday_to_room_to_slots[slot.weekday][slot.room].append((i, slot))
        self.graph.create_graph(vertices_number)
        for weekday in weekday_to_room_to_slots:
            for room, lessons in weekday_to_room_to_slots[weekday].items():
                lessons: list[tuple[int, LessonWithExcelCellsDTO]]
                if self.is_online_slot(room):
                    logger.info("No need to check room collision for online")
                    continue

                if len(lessons) == 1:
                    logger.info(
                        f"Room {room} has only one lesson on {weekday}"
                    )
                    continue

                for i, (ind1, lesson1) in enumerate(lessons):
                    if (
                        lesson1.lesson_name
                        == "Elective course on Physical Education"
                    ):
                        logger.info("Skip Physical Education")
                        continue
                    for j in range(i + 1, len(lessons)):
                        ind2, lesson2 = lessons[j]
                        if (
                            lesson2.lesson_name
                            == "Elective course on Physical Education"
                        ):
                            logger.info("Skip Physical Education")
                            continue

                        if self.check_two_timeslots_collisions_by_time(
                            lesson1, lesson2
                        ):
                            self.graph.add_edge(ind1, ind2)
        connected_components = self.graph.get_connected_components()
        collisions = self.get_colliding_timeslots(
            timeslots, connected_components, CollisionTypeEnum.ROOM
        )
        logger.info(
            f"Total collisions: {len(collisions)}: {pprint.pformat(collisions)}"
        )
        return collisions

    def get_collisions_by_teacher(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        teachers_to_timeslots: dict[
            str, list[tuple[int, LessonWithExcelCellsDTO]]
        ] = defaultdict(list)
        self.graph.create_graph(len(timeslots))
        for i, obj in enumerate(timeslots):
            teachers_to_timeslots[obj.teacher].append((i, obj))
            if isinstance(obj.group_name, str):
                if (
                    obj.teacher
                    in self.group_to_studying_teachers[obj.group_name]
                ):
                    teachers_to_timeslots[obj.teacher].append((i, obj))
                continue
            for group_name in obj.group_name:
                if obj.teacher in self.group_to_studying_teachers[group_name]:
                    teachers_to_timeslots[obj.teacher].append((i, obj))
        for teacher in teachers_to_timeslots:
            n = len(teachers_to_timeslots[teacher])
            for i in range(n):
                ind1, slot1 = teachers_to_timeslots[teacher][i]
                for j in range(i + 1, n):
                    ind2, slot2 = teachers_to_timeslots[teacher][j]
                    if slot1.weekday != slot2.weekday:
                        continue
                    if self.check_two_timeslots_collisions_by_time(
                        slot1, slot2
                    ):
                        self.graph.add_edge(ind1, ind2)
        connected_components = self.graph.get_connected_components()
        return self.get_colliding_timeslots(
            timeslots, connected_components, CollisionTypeEnum.TEACHER
        )

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
        today = datetime.datetime.now(pytz.utc).date()

        for lesson in timeslots:
            start_datetime = datetime.datetime.combine(
                today, lesson.start_time
            )
            end_datetime = datetime.datetime.combine(
                today + datetime.timedelta(days=30), lesson.end_time
            )
            min_needed_time = min(start_datetime, min_needed_time)
            max_needed_time = max(end_datetime, max_needed_time)

        try:
            all_bookings = await self.booking_service.get_all_bookings(
                start=min_needed_time, end=max_needed_time
            )
        except Exception as e:
            logger.warning(f"Error while fetching bookings: {e}")
            return []

        collisions = []

        weekday_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        valid_rooms = {room.id for room in self.rooms}

        for lesson in timeslots:
            if self.is_online_slot(lesson) or lesson.room not in valid_rooms:
                continue

            lesson_weekday = weekday_map.get(lesson.weekday.lower())
            if lesson_weekday is None:
                continue

            lesson_dates = []

            for day_offset in range(
                30
            ):  # TODO: Change fixed 30-day window to semester based window
                check_date = today + datetime.timedelta(days=day_offset)
                if check_date.weekday() == lesson_weekday:
                    lesson_dates.append(check_date)

            lesson_collisions = [
                LessonWithCollisionTypeDTO(
                    **lesson.model_dump(),
                    collision_type=CollisionTypeEnum.OUTLOOK,
                )
            ]

            for lesson_date in lesson_dates:
                lesson_start = datetime.datetime.combine(
                    lesson_date, lesson.start_time
                ).replace(tzinfo=pytz.utc)
                lesson_end = datetime.datetime.combine(
                    lesson_date, lesson.end_time
                ).replace(tzinfo=pytz.utc)

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
                    if (
                        booking.title.lower().strip()
                        == lesson.lesson_name.lower().strip()
                    ):
                        continue

                    if (
                        booking.start_time < lesson_end
                        and booking.end_time > lesson_start
                    ):
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

    def _sort_by_weekday_and_end_time(
        self, collisions: list[LessonWithExcelCellsDTO]
    ) -> tuple:
        first_attr = collisions[0].weekday
        second_attr = collisions[0].end_time
        return (
            Weekdays.__members__.get(first_attr, Weekdays.SUNDAY).value,
            second_attr,
        )

    def sort_collisions(
        self, collisions: list[LessonWithExcelCellsDTO]
    ) -> None:
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
            logger.info(f"Room collisions ({len(_)}): {pprint.pformat(_)}")
            collisions.extend(_)
        if check_teacher_collisions:
            collisions.extend(self.get_collisions_by_teacher(timeslots))
        if check_space_collisions:
            collisions.extend(
                self.get_lessons_where_not_enough_place_for_students(timeslots)
            )
        if check_outlook_collisions:
            collisions.extend(await self.get_outlook_collisions(timeslots))
        self.sort_collisions(collisions)
        return collisions
