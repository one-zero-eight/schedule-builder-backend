from collections import defaultdict

from src.domain.dtos.collisions import CollisionsDTO
from src.domain.dtos.lesson import (
    LessonWithCollisionsDTO,
    LessonWithTeacherAndGroup,
)
from src.domain.dtos.teacher import TeacherDTO
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


class CollisionsChecker(ICollisionsChecker):
    def __init__(
        self, parser: ICoursesParser, teachers: list[TeacherDTO]
    ) -> None:
        self.parser = parser
        self.teachers = teachers
        self.group_to_studying_teachers = defaultdict(list)
        for teacher in teachers:
            self.group_to_studying_teachers[teacher.group].append(teacher)

    def check_two_timeslots_collisions_by_time(
        self,
        slot1: LessonWithTeacherAndGroup,
        slot2: LessonWithTeacherAndGroup,
    ) -> bool:
        if (
            slot2.start < slot1.start < slot2.end
            or slot2.start < slot1.end < slot2.end
        ):
            return True
        if (
            slot1.start < slot2.start < slot1.end
            or slot1.start < slot2.end < slot1.end
        ):
            return True
        return False

    def is_online_slot(self, slot: LessonWithTeacherAndGroup) -> bool:
        return "ONLINE" == slot.room

    def get_collsisions_by_room(
        self, timeslots: list[LessonWithTeacherAndGroup]
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
                        slot2 = weekday_to_room_to_slots[weekday][room][j]
                        if self.is_online_slot(slot2):
                            continue
                        if self.check_two_timeslots_collisions_by_time(
                            slot1, slot2
                        ):
                            slot_with_collisions.collisions.append(slot2)
                    if slot_with_collisions.collisions:
                        collisions.append(slot_with_collisions)
        return collisions

    def get_collisions_by_teacher(
        self, timeslots: list[LessonWithTeacherAndGroup]
    ) -> list[LessonWithCollisionsDTO]:
        collisions: list[LessonWithCollisionsDTO] = list()
        teachers_to_timeslots: dict[str, list[LessonWithTeacherAndGroup]] = (
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
                    slot2 = teachers_to_timeslots[teacher][j]
                    if self.check_two_timeslots_collisions_by_time(
                        slot1, slot2
                    ):
                        slot_with_collisions.collisions.append(slot2)
                if slot_with_collisions.collisions:
                    collisions.append(slot_with_collisions)
        return collisions

    async def get_collisions(self, spreadsheet_id: str) -> dict[
        str,
        list[LessonWithCollisionsDTO],
    ]:
        timeslots: list[LessonWithTeacherAndGroup] = (
            await self.parser.get_all_timeslots(spreadsheet_id)
        )
        collisions = CollisionsDTO(
            rooms=self.get_collsisions_by_room(timeslots),
            teachers=self.get_collisions_by_teacher(timeslots),
        )
        return collisions
