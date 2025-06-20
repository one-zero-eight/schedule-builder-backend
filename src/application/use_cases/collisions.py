from collections import defaultdict
from datetime import datetime, timedelta

import pytz

from src.application.external_api.innohassle.interfaces.booking import (
    IBookingService,
)
from src.domain.dtos.collisions import CollisionsDTO
from src.domain.dtos.lesson import (
    BaseLessonDTO,
    LessonWithCollisionsDTO,
    LessonWithExcelCells,
    LessonWithOutlookCollisionsDTO,
    LessonWithTeacherAndGroup,
)
from src.domain.dtos.room import RoomDTO
from src.domain.dtos.teacher import TeacherDTO
from src.domain.enums import CollisionTypeEnum
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


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
        if (
            slot2.start_time < slot1.start_time < slot2.end_time
            or slot2.start_time < slot1.end_time < slot2.end_time
        ):
            return True
        if (
            slot1.start_time < slot2.start_time < slot1.end_time
            or slot1.start_time < slot2.end_time < slot1.end_time
        ):
            return True
        return False

    def is_online_slot(self, slot: BaseLessonDTO) -> bool:
        return "ONLINE" == slot.room

    def get_collsisions_by_room(
        self, timeslots: list[LessonWithExcelCellsDTO]
    ) -> list[LessonWithCollisionsDTO]:
        weekday_to_room_to_slots = defaultdict(lambda: defaultdict(list))
        for slot in timeslots:
            weekday_to_room_to_slots[slot.weekday][slot.room].append(slot)
        collisions = []
        for weekday in weekday_to_room_to_slots:
            for room in weekday_to_room_to_slots[weekday]:
                n = len(weekday_to_room_to_slots[weekday][room])
                for i in range(n):
                    slot1 = weekday_to_room_to_slots[weekday][room][i]
                    slot_with_collisions = (
                        LessonWithCollisionsDTO.model_validate(
                            slot1, from_attributes=True
                        )
                    )
                    if self.is_online_slot(slot1):
                        continue
                    for j in range(i + 1, n):
                        slot2: LessonWithExcelCellsDTO = (
                            weekday_to_room_to_slots[weekday][room][j]
                        )
                        if self.is_online_slot(slot2):
                            continue
                        if self.check_two_timeslots_collisions_by_time(
                            slot1, slot2
                        ):
                            slot_with_collisions.collisions.append(
                                LessonWithCollisionTypeDTO(
                                    **slot2.model_dump(),
                                    collision_type=CollisionTypeEnum.ROOM,
                                )
                            )
                    if slot_with_collisions.collisions:
                        collisions.append(slot_with_collisions)
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
            if obj.teacher in self.group_to_studying_teachers[obj.group_name]:
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

    def get_outlook_collisions(
        self, timeslots: list[LessonWithExcelCells]
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

            today = datetime.now(pytz.utc).date()
            lesson_dates = []

            for day_offset in range(
                30
            ):  # TODO: Change fixed 30-day window to semester based window
                check_date = today + timedelta(days=day_offset)
                if check_date.weekday() == lesson_weekday:
                    lesson_dates.append(check_date)

            lesson_collisions = []

            for lesson_date in lesson_dates:
                lesson_start = datetime.combine(
                    lesson_date, lesson.start
                ).replace(tzinfo=pytz.utc)
                lesson_end = datetime.combine(lesson_date, lesson.end).replace(
                    tzinfo=pytz.utc
                )

                try:
                    bookings = self.booking_service.get_bookings(
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
                        booking.start < lesson_end
                        and booking.end > lesson_start
                    ):
                        booking_as_lesson = LessonWithTeacherAndGroup(
                            lesson_name=booking.title,
                            weekday=lesson.weekday,
                            start=booking.start.time(),
                            end=booking.end.time(),
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
                    start=lesson.start,
                    end=lesson.end,
                    room=lesson.room,
                    teacher=lesson.teacher,
                    group_name=lesson.group_name,
                    students_number=lesson.students_number,
                    collisions=lesson_collisions,
                )
                collisions.append(outlook_collision)

        return collisions

    async def get_collisions(self, spreadsheet_id: str) -> CollisionsDTO:
        timeslots: list[LessonWithExcelCells] = (
            await self.parser.get_all_timeslots(spreadsheet_id)
        )
        collisions = CollisionsDTO(
            rooms=self.get_collsisions_by_room(timeslots),
            teachers=self.get_collisions_by_teacher(timeslots),
            capacity=self.get_lessons_where_not_enough_place_for_students(
                timeslots
            ),
            outlook=self.get_outlook_collisions(timeslots),
        )
        return collisions
