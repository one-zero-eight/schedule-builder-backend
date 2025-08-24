from fastapi import APIRouter

from src.api.dependencies import VerifyTokenDep
from src.modules.bookings.client import booking_client
from src.modules.collisions.collision_checker import CollisionChecker
from src.modules.collisions.schemas import CheckResults
from src.modules.options.repository import options_repository
from src.modules.parsers.core_courses.parser import CoreCoursesParser

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
    target_sheet_names: list[str],
    check_room_collisions: bool = True,
    check_teacher_collisions: bool = True,
    check_space_collisions: bool = True,
    check_outlook_collisions: bool = True,
) -> CheckResults:
    user, token = user_and_token
    parser = CoreCoursesParser()
    lessons = await parser.get_all_lessons(
        google_spreadsheet_id,
        target_sheet_names,
    )

    teachers_data = options_repository.get_teachers()
    if teachers_data is None:
        teachers = []
    else:
        teachers = teachers_data.data

    collisions_use_case = CollisionChecker(
        token=token,
        rooms=await booking_client.get_rooms(token),
        teachers=teachers,
    )

    issues = await collisions_use_case.get_collisions(
        lessons,
        check_room_collisions=check_room_collisions,
        check_teacher_collisions=check_teacher_collisions,
        check_space_collisions=check_space_collisions,
        check_outlook_collisions=check_outlook_collisions,
    )

    return CheckResults(issues=issues)
