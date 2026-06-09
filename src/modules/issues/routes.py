from fastapi import APIRouter

from src.api.dependencies import VerifyTokenDep
from src.logging_ import logger
from src.modules.issues import service
from src.modules.issues.schemas import CheckParameters, CheckResults

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post(
    "/check",
    responses={
        200: {"description": "Schedule issues"},
        401: {"description": "Invalid token OR no credentials provided"},
    },
)
async def check_schedule_issues(user_and_token: VerifyTokenDep, params: CheckParameters) -> CheckResults:
    logger.info(f"Checking schedule issues with options: {params}")
    _user, token = user_and_token
    return await service.check_schedule_issues(token, params)
