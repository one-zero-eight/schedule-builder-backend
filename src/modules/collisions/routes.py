from fastapi import APIRouter

from src.api.dependencies import VerifyTokenDep
from src.core_courses.config import CoreCoursesConfig
from src.core_courses.config import Tag as CoreCoursesTag
from src.custom_pydantic import CustomModel
from src.electives.config import ElectivesParserConfig
from src.electives.config import Tag as ElectivesTag
from src.logging_ import logger
from src.modules.bookings.client import booking_client
from src.modules.collisions.collision_checker import CollisionChecker
from src.modules.collisions.core_courses_adapter import get_all_core_courses_lessons
from src.modules.collisions.electives_adapter import get_all_electives_lessons
from src.modules.collisions.schemas import CheckResults
from src.modules.options.repository import options_repository

router = APIRouter(prefix="/collisions", tags=["Collisions"])


class CheckParameters(CustomModel):
    care_about_core_courses: bool = True
    care_about_electives: bool = True

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
async def check_timetable_collisions(user_and_token: VerifyTokenDep, params: CheckParameters) -> CheckResults:
    logger.info(f"Checking timetable collisions with options: {params}")
    user, token = user_and_token

    semester_options = options_repository.get_semester()
    if not semester_options or not semester_options.core_courses_spreadsheet_id:
        raise ValueError("core_courses_spreadsheet_id must be set in semester options")
    logger.info(f"Semester options: {semester_options}")

    if semester_options.core_courses_spreadsheet_id and params.care_about_core_courses:
        core_courses_lessons = await get_all_core_courses_lessons(
            CoreCoursesConfig(
                targets=semester_options.core_courses_targets,
                spreadsheet_id=semester_options.core_courses_spreadsheet_id,
                semester_tag=CoreCoursesTag(alias="", type="", name=""),
            ),
        )
    else:
        core_courses_lessons = []
    logger.info(f"Found {len(core_courses_lessons)} core courses lessons")

    if semester_options.electives_spreadsheet_id and params.care_about_electives:
        electives_lessons = await get_all_electives_lessons(
            ElectivesParserConfig(
                targets=semester_options.electives_targets,
                spreadsheet_id=semester_options.electives_spreadsheet_id,
                semester_tag=ElectivesTag(alias="", type="", name=""),
                electives=semester_options.electives,
            ),
        )
    else:
        electives_lessons = []
    logger.info(f"Found {len(electives_lessons)} electives lessons")

    teachers_data = options_repository.get_teachers()
    if teachers_data is None:
        teachers = []
    else:
        teachers = teachers_data.data
    logger.info(f"Found {len(teachers)} teachers")

    collisions_use_case = CollisionChecker(
        token=token,
        rooms=await booking_client.get_rooms(token),
        teachers=teachers,
        very_same_lessons=semester_options.very_same_lessons,
    )

    issues = await collisions_use_case.get_collisions(
        core_courses_lessons + electives_lessons,
        targets=[*semester_options.core_courses_targets, *semester_options.electives_targets],
        check_room_collisions=params.check_room_collisions,
        check_teacher_collisions=params.check_teacher_collisions,
        check_space_collisions=params.check_space_collisions,
        check_outlook_collisions=params.check_outlook_collisions,
    )

    return CheckResults(issues=issues)
