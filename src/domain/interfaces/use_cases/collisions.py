from abc import ABC, abstractmethod

from src.domain.dtos.lesson import LessonWithCollisionTypeDTO


class ICollisionsUseCase(ABC):
    @abstractmethod
    async def get_collisions(
        self,
        spreadsheet_id: str,
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        pass
