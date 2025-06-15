from dishka import Provider, Scope, provide
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.external_api.innohassle.interfaces.token_manager import (
    ITokenManager,
)
from src.domain.dtos.users import UserTokenDataDTO
from src.domain.exceptions.tokens import InvalidTokenException


class UserTokenDataProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def verify_user(
        self,
        request: Request,
        token_manager: ITokenManager,
    ) -> UserTokenDataDTO:
        token = request.headers.get("Authorization").split()[1]
        if not token:
            raise InvalidTokenException()
        return await token_manager.verify_user_token(token)
