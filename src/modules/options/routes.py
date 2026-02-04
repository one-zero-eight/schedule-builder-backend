from fastapi import APIRouter, Body

from src.api.dependencies import VerifyTokenDep
from src.modules.options.repository import OptionsData, SemesterOptions, TeachersData, options_repository

router = APIRouter(prefix="/options", tags=["Options"])


@router.post("/set-semester")
async def set_semester(_user_and_token: VerifyTokenDep, data: SemesterOptions) -> SemesterOptions:
    options_repository.set_semester(data)
    return data


@router.get("/semester")
async def get_semester(_user_and_token: VerifyTokenDep) -> SemesterOptions | None:
    return options_repository.get_semester()


@router.get("/")
async def get_all_options(_user_and_token: VerifyTokenDep) -> OptionsData:
    return options_repository.get_all_options()


@router.post("/set-teachers")
async def set_teachers(
    _user_and_token: VerifyTokenDep,
    csv_text: str = Body(
        media_type="text/tab-separated-values",
    ),
) -> TeachersData:
    data = options_repository.set_teachers_from_csv_text(csv_text)
    return data


@router.get("/teachers")
async def get_teachers(_user_and_token: VerifyTokenDep) -> TeachersData | None:
    return options_repository.get_teachers()
