from src.domain.dtos.lesson import LessonWithCollisionTypeDTO
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)
from src.domain.interfaces.services.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsUseCase


class CollisionsUseCase(ICollisionsUseCase):
    def __init__(
        self, parser: ICoursesParser, collisions_checker: ICollisionsChecker
    ) -> None:
        self.parser = parser
        self.collisions_checker = collisions_checker

    async def get_collisions(
        self,
        spreadsheet_id: str,
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ) -> list[list[LessonWithCollisionTypeDTO]]:
        timeslots = await self.parser.get_all_timeslots(spreadsheet_id)
        return await self.collisions_checker.get_collisions(
            timeslots,
            check_room_collisions,
            check_teacher_collisions,
            check_space_collisions,
            check_outlook_collisions,
        )
