from abc import ABC, abstractmethod

from src.domain.dtos.lesson import (
    LessonWithCollisionTypeDTO,
    LessonWithDateDTO,
)


class ICollisionsChecker(ABC):
    @abstractmethod
    async def get_collisions(
        self,
        timeslots: list[LessonWithDateDTO],
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass

    @abstractmethod
    async def get_outlook_collisions(
        self, timeslots: list[LessonWithDateDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass

    @abstractmethod
    def get_lessons_where_not_enough_place_for_students(
        self, timeslots: list[LessonWithDateDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass

    @abstractmethod
    def get_collisions_by_teacher(
        self, timeslots: list[LessonWithDateDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass

    @abstractmethod
    def get_collisions_by_room(
        self, timeslots: list[LessonWithDateDTO]
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass
