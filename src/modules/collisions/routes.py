from fastapi import APIRouter

from src.api.dependencies import VerifyTokenDep
from src.config import settings
from src.logging_ import logger
from src.modules.bookings.client import booking_client
from src.modules.collisions.collision_checker import CollisionChecker, LessonWithCollisionTypeDTO
from src.modules.collisions.graph import UndirectedGraph
from src.modules.parsers.core_courses.parser import CoreCoursesParser
from src.modules.parsers.utils import sanitize_sheet_name

router = APIRouter(prefix="/collisions", tags=["Collisions"])


@router.get(
    "/check",
    responses={
        200: {"description": "Timetable collisions"},
        401: {"description": "Invalid token OR no credentials provided"},
    },
)
async def check_timetable_collisions(
    user_and_token: VerifyTokenDep,
    google_spreadsheet_id: str,
    target_sheet_name: str | None = None,
    check_room_collisions: bool = True,
    check_teacher_collisions: bool = True,
    check_space_collisions: bool = True,
    check_outlook_collisions: bool = True,
) -> list[list[LessonWithCollisionTypeDTO]]:
    user, token = user_and_token
    collisions_use_case = CollisionChecker(
        token=token,
        rooms=await booking_client.get_rooms(token),
        teachers=settings.teachers,
        graph=UndirectedGraph(),
    )
    targets = settings.core_courses_config.targets
    if target_sheet_name:
        for target in targets:
            if sanitize_sheet_name(target.sheet_name) == sanitize_sheet_name(target_sheet_name):
                targets = [target]
                logger.info(f"Hit target sheet name: {target.sheet_name}")
                break
    parser = CoreCoursesParser(targets=targets)
    timeslots = await parser.get_all_timeslots(google_spreadsheet_id)
    return await collisions_use_case.get_collisions(
        timeslots,
        check_room_collisions=check_room_collisions,
        check_teacher_collisions=check_teacher_collisions,
        check_space_collisions=check_space_collisions,
        check_outlook_collisions=check_outlook_collisions,
    )
