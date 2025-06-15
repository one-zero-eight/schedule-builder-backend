import asyncio

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.domain.dtos.collisions import CollisionsDTO
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


router = APIRouter(prefix="/collisions", route_class=DishkaRoute)


@router.get("/check")
async def check_timetable_collisions(
    google_spreadsheet_id: str,
    collisions_checker: FromDishka[ICollisionsChecker],
    parser: FromDishka[ICoursesParser],
) -> CollisionsDTO:
    return collisions_checker.get_collisions(
        await parser.get_all_timeslots(google_spreadsheet_id)
    )
