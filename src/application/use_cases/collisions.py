import datetime
import pprint
from collections import defaultdict
from typing import Literal

import pytz

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.lesson import (
    BaseLessonDTO,
    LessonWithCollisionsDTO,
    LessonWithCollisionTypeDTO,
    LessonWithExcelCellsDTO,
    LessonWithOutlookCollisionsDTO,
    LessonWithTeacherAndGroupDTO,
)
from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.enums import CollisionTypeEnum
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker
from src.logging_ import logger


class CollisionsChecker(ICollisionsChecker):
    def __init__(
        self,
        parser: ICoursesParser,
        teachers: list[TeacherDTO],
        rooms: list[RoomDTO],
        booking_service: IBookingService,
    ) -> None:
        self.parser = parser
        self.teachers = teachers
        self.rooms = rooms
        self.booking_service = booking_service
        self.group_to_studying_teachers = defaultdict(list)
        for teacher in teachers:
            self.group_to_studying_teachers[teacher.group].append(teacher)
        self.room_to_capacity = dict()
        for room in rooms:
            self.room_to_capacity[room.id] = room.capacity

    def check_two_timeslots_collisions_by_time(
        self,
        slot1: BaseLessonDTO,
        slot2: BaseLessonDTO,
    ) -> bool:
        if (slot1.end_time < slot2.start_time) or (
            slot1.start_time > slot2.end_time
        ):
            return False
        return True

    def is_online_slot(self, slot_or_room: BaseLessonDTO | str) -> bool:
        if isinstance(slot_or_room, str):
            return "ONLINE" == slot_or_room
        return "ONLINE" == slot_or_room.room

    def get_collsisions_by_room(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[LessonWithCollisionsDTO]:
        weekday_to_room_to_slots = defaultdict(lambda: defaultdict(list))
        for slot in timeslots:
            weekday_to_room_to_slots[slot.weekday][slot.room].append(slot)
        collisions = []
        for weekday in weekday_to_room_to_slots:
            for room, lessons in weekday_to_room_to_slots[weekday].items():
                lessons: list[LessonWithExcelCellsDTO]
                if self.is_online_slot(room):
                    logger.info("No need to check room collision for online")
                    continue

                if len(lessons) == 1:
                    logger.info(
                        f"Room {room} has only one lesson on {weekday}"
                    )
                    continue

                for i, lesson1 in enumerate(lessons):
                    if (
                        lesson1.lesson_name
                        == "Elective course on Physical Education"
                    ):
                        logger.info("Skip Physical Education")
                        continue
                    slot_with_collisions = (
                        LessonWithCollisionsDTO.model_validate(
                            lesson1, from_attributes=True
                        )
                    )
                    for lesson2 in lessons[i + 1 :]:
                        if (
                            lesson2.lesson_name
                            == "Elective course on Physical Education"
                        ):
                            logger.info("Skip Physical Education")
                            continue

                        if self.check_two_timeslots_collisions_by_time(
                            lesson1, lesson2
                        ):
                            # double check if they are exact
                            if (
                                lesson1.lesson_name == lesson2.lesson_name
                                and lesson1.teacher == lesson2.teacher
                                and lesson1.room == lesson2.room
                            ):
                                pass
                            slot_with_collisions.collisions.append(
                                LessonWithCollisionTypeDTO(
                                    **lesson2.model_dump(),
                                    collision_type=CollisionTypeEnum.ROOM,
                                )
                            )
                    if slot_with_collisions.collisions:
                        collisions.append(slot_with_collisions)
        logger.info(
            f"Total collisions: {len(collisions)}: {pprint.pformat(collisions)}"
        )
        return collisions

    def get_collisions_by_teacher(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[LessonWithCollisionsDTO]:
        collisions: list[LessonWithCollisionsDTO] = list()
        teachers_to_timeslots: dict[str, list[LessonWithExcelCellsDTO]] = (
            defaultdict(list)
        )
        for obj in timeslots:
            teachers_to_timeslots[obj.teacher].append(obj)
            if isinstance(obj.group_name, str):
                if (
                    obj.teacher
                    in self.group_to_studying_teachers[obj.group_name]
                ):
                    teachers_to_timeslots[obj.teacher].append(obj)
                continue
            for group_name in obj.group_name:
                if obj.teacher in self.group_to_studying_teachers[group_name]:
                    teachers_to_timeslots[obj.teacher].append(obj)
        for teacher in teachers_to_timeslots:
            n = len(teachers_to_timeslots[teacher])
            for i in range(n):
                slot1 = teachers_to_timeslots[teacher][i]
                slot_with_collisions = LessonWithCollisionsDTO.model_validate(
                    slot1, from_attributes=True
                )
                for j in range(i + 1, n):
                    slot2: LessonWithExcelCellsDTO = teachers_to_timeslots[
                        teacher
                    ][j]
                    if self.check_two_timeslots_collisions_by_time(
                        slot1, slot2
                    ):
                        slot_with_collisions.collisions.append(
                            LessonWithCollisionTypeDTO(
                                **slot2.model_dump(),
                                collision_type=CollisionTypeEnum.TEACHER,
                            )
                        )
                if slot_with_collisions.collisions:
                    collisions.append(slot_with_collisions)
        return collisions

    def get_lessons_where_not_enough_place_for_students(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[LessonWithExcelCellsDTO]:
        result = []
        for timeslot in timeslots:
            if self.is_online_slot(timeslot):
                continue
            room = timeslot.room
            capacity = self.room_to_capacity.get(room)
            if not capacity:
                continue
            if capacity < timeslot.students_number:
                result.append(
                    LessonWithCollisionTypeDTO(
                        **timeslot.model_dump(),
                        collision_type=CollisionTypeEnum.CAPACITY,
                    )
                )
        return result

    async def get_outlook_collisions(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[LessonWithOutlookCollisionsDTO]:
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

            today = datetime.datetime.now(pytz.utc).date()
            lesson_dates = []

            for day_offset in range(
                30
            ):  # TODO: Change fixed 30-day window to semester based window
                check_date = today + datetime.timedelta(days=day_offset)
                if check_date.weekday() == lesson_weekday:
                    lesson_dates.append(check_date)

            lesson_collisions = []

            for lesson_date in lesson_dates:
                lesson_start = datetime.datetime.combine(
                    lesson_date, lesson.start_time
                ).replace(tzinfo=pytz.utc)
                lesson_end = datetime.datetime.combine(
                    lesson_date, lesson.end_time
                ).replace(tzinfo=pytz.utc)

                try:
                    bookings = await self.booking_service.get_bookings(
                        room_id=lesson.room, start=lesson_start, end=lesson_end
                    )
                except Exception:
                    # TODO: add logging once logger is added
                    continue

                for booking in bookings:
                    if (
                        booking.title.lower().strip()
                        == lesson.lesson_name.lower().strip()
                    ):
                        continue

                    if (
                        booking.start_time < lesson_end
                        and booking.end_time > lesson_start
                    ):
                        booking_as_lesson = LessonWithTeacherAndGroupDTO(
                            lesson_name=booking.title,
                            weekday=lesson.weekday,
                            start_time=booking.start_time.time(),
                            end_time=booking.end_time.time(),
                            room=lesson.room,
                            teacher="External Booking",  # Placeholder
                            group_name=None,
                            students_number=0,
                        )

                        if booking_as_lesson not in lesson_collisions:
                            lesson_collisions.append(booking_as_lesson)

            if lesson_collisions:
                outlook_collision = LessonWithOutlookCollisionsDTO(
                    lesson_name=lesson.lesson_name,
                    weekday=lesson.weekday,
                    start_time=lesson.start_time,
                    end_time=lesson.end_time,
                    room=lesson.room,
                    teacher=lesson.teacher,
                    group_name=lesson.group_name,
                    students_number=lesson.students_number,
                    collisions=lesson_collisions,
                )
                collisions.append(outlook_collision)

        return collisions

    async def get_collisions(
        self,
        spreadsheet_id: str,
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[LessonWithCollisionsDTO | LessonWithCollisionTypeDTO]:
        timeslots: list[LessonWithExcelCellsDTO] = (
            await self.parser.get_all_timeslots(spreadsheet_id)
        )
        logger.info(f"{len(timeslots)} Timeslots")
        collisions = []

        if check_room_collisions:
            _ = self.get_collsisions_by_room(timeslots)
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
        return collisions
