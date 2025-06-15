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

    @provide(scope=Scope.APP)
    def get_bearer_scheme(self) -> HTTPBearer:
        return HTTPBearer(
            scheme_name="Bearer",
            description="Token from [InNoHassle Accounts](https://api.innohassle.ru/accounts/v0/tokens/generate-my-token)",
            bearerFormat="JWT",
            auto_error=False,
        )

    @provide
    async def get_credentials(
        self, request: Request, bearer: HTTPBearer
    ) -> HTTPAuthorizationCredentials:
        return await bearer(request)

    @provide
    async def verify_user(
        self, bearer: HTTPAuthorizationCredentials, token_manager: ITokenManager
    ) -> UserTokenDataDTO:
        token = bearer and bearer.credentials
        if not token:
            raise InvalidTokenException()
        return await token_manager.verify_user_token(token)
