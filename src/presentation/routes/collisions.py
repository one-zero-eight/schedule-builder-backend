from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.domain.dtos.lesson import (
    LessonWithCollisionsDTO,
    LessonWithCollisionTypeDTO,
)
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


router = APIRouter(
    prefix="/collisions", route_class=DishkaRoute, tags=["Collisions"]
)


@router.get("/check")
async def check_timetable_collisions(
    google_spreadsheet_id: str,
    collisions_checker: FromDishka[ICollisionsChecker],
    check_room_collisions: bool = True,
    check_teacher_collisions: bool = True,
    check_space_collisions: bool = True,
    check_outlook_collisions: bool = True,
) -> list[LessonWithCollisionsDTO | LessonWithCollisionTypeDTO]:
    return await collisions_checker.get_collisions(
        google_spreadsheet_id,
        check_room_collisions=check_room_collisions,
        check_teacher_collisions=check_teacher_collisions,
        check_space_collisions=check_space_collisions,
        check_outlook_collisions=check_outlook_collisions,
    )
