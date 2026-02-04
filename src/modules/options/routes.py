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
    csv_text: str = Body(media_type="text/tab-separated-values"),
) -> TeachersData:
    """
    Upload teachers data from TSV (tab-separated values).

    Expected columns (case-insensitive):
    - Name - teacher's full name in English
    - Russian Name (or ФИО/Имя) - teacher's full name in Russian
    - Alias (or Telegram) - short name or telegram handle
    - Email - email address
    - Student Group (or Student?) - student group code (e.g. "B24-CSE-05", "M25-SE-01")

    Example:
    ```
    Name\tRussian Name\tAlias\tEmail\tStudent Group
    Ivan Ivanov\tИванов Иван Иванович\t@ivanov\tivanov@example.com\t
    Petr Petrov\tПетров Петр Петрович\t-\tpetrov@example.com\tB24-CSE-05
    ```
    """
    data = options_repository.set_teachers_from_csv_text(csv_text)
    return data


@router.get("/teachers")
async def get_teachers(_user_and_token: VerifyTokenDep) -> TeachersData | None:
    return options_repository.get_teachers()
