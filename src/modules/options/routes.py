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
        description="""Tab-separated values with columns: Name, Alias, Email, Student Group.

Example:
```
Name\tAlias\tEmail\tStudent Group
Иванов Иван Иванович\tIvanov I.\tivanov@example.com\t
Петров Петр Петрович\t-\tpetrov@example.com\tB4-CSE-05
```

Student Group format: B4-CSE-05 (year-program-group number)
""",
    ),
) -> TeachersData:
    """
    Upload teachers data from TSV (tab-separated values).

    Expected columns:
    - Name (or unnamed first column) - teacher's full name
    - Alias - short name (use "-" or "?" for none)
    - Email - email address
    - Student Group - student group code if teacher is a student (e.g. "B4-CSE-05")
    """
    data = options_repository.set_teachers_from_csv_text(csv_text)
    return data


@router.get("/teachers")
async def get_teachers(_user_and_token: VerifyTokenDep) -> TeachersData | None:
    return options_repository.get_teachers()
