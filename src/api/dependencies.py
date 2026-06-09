__all__ = ["ModeratorDep", "VerifyTokenDep", "is_moderator_email", "verify_moderator_dep", "verify_token_dep"]

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings
from src.modules.inh_accounts_sdk import UserTokenData, inh_accounts

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Token from [InNoHassle Accounts](https://innohassle.ru/account/token)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def verify_token_dep(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> tuple[UserTokenData, str] | None:
    # Prefer header to cookie
    token = bearer and bearer.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = inh_accounts.decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data, token


VerifyTokenDep = Annotated[tuple[UserTokenData, str], Depends(verify_token_dep)]
"""
Dependency for verifying the user token.
"""


def is_moderator_email(email: str) -> bool:
    normalized = email.casefold()
    return any(moderator_email.casefold() == normalized for moderator_email in settings.moderator_emails)


async def verify_moderator_dep(
    user_and_token: VerifyTokenDep,
) -> tuple[UserTokenData, str]:
    user, token = user_and_token
    if not is_moderator_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a moderator",
        )
    return user, token


ModeratorDep = Annotated[tuple[UserTokenData, str], Depends(verify_moderator_dep)]
"""
Dependency for verifying the user token and moderator access.
"""
