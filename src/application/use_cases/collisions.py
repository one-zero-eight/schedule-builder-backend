from src.domain.dtos.lesson import LessonWithCollisionTypeDTO


class CollisionsUseCase:
    def __init__(
        self, parser, collisions_checker
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
