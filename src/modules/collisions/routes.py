from fastapi import APIRouter

from src.api.dependencies import VerifyTokenDep
from src.core_courses.config import CoreCoursesConfig, Tag
from src.custom_pydantic import CustomModel
from src.modules.bookings.client import booking_client
from src.modules.collisions.collision_checker import CollisionChecker
from src.modules.collisions.core_courses_adapter import get_all_lessons
from src.modules.collisions.schemas import CheckResults
from src.modules.options.repository import options_repository

router = APIRouter(prefix="/collisions", tags=["Collisions"])


class CheckParameters(CustomModel):
    check_room_collisions: bool = True
    check_teacher_collisions: bool = True
    check_space_collisions: bool = True
    check_outlook_collisions: bool = True


@router.post(
    "/check",
    responses={
        200: {"description": "Timetable collisions"},
        401: {"description": "Invalid token OR no credentials provided"},
    },
)
async def check_timetable_collisions(
    user_and_token: VerifyTokenDep,
    params: CheckParameters,
) -> CheckResults:
    user, token = user_and_token

    semester_options = options_repository.get_semester()
    if not semester_options or not semester_options.core_courses_spreadsheet_id:
        raise ValueError("core_courses_spreadsheet_id must be set in semester options")

    targets = semester_options.core_courses_targets
    spreadsheet_id = semester_options.core_courses_spreadsheet_id

    lessons = await get_all_lessons(
        CoreCoursesConfig(
            targets=targets,
            spreadsheet_id=spreadsheet_id,
            semester_tag=Tag(alias="", type="", name=""),
        ),
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
        targets=targets,
        check_room_collisions=params.check_room_collisions,
        check_teacher_collisions=params.check_teacher_collisions,
        check_space_collisions=params.check_space_collisions,
        check_outlook_collisions=params.check_outlook_collisions,
    )

    return CheckResults(issues=issues)
