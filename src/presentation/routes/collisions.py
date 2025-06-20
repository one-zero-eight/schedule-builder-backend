from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.domain.dtos.collisions import CollisionsDTO
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


router = APIRouter(
    prefix="/collisions", route_class=DishkaRoute, tags=["Collisions"]
)


@router.get("/check")
async def check_timetable_collisions(
    google_spreadsheet_id: str,
    collisions_checker: FromDishka[ICollisionsChecker],
) -> CollisionsDTO:
    return await collisions_checker.get_collisions(google_spreadsheet_id)
