from dishka import Provider, Scope, provide
from fastapi import Request

from src.config import DEBUG
from src.domain.dtos.users import UserTokenDataDTO
from src.domain.exceptions.tokens import InvalidTokenException
from src.infrastructure.external_api.innohassle.token_manager import TokenManager


class UserTokenDataProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def verify_user(
        self,
        request: Request,
        token_manager: TokenManager,
    ) -> UserTokenDataDTO:
        if DEBUG:
            return UserTokenDataDTO(innohassle_id="1", token="token")
        token = request.headers.get("Authorization")
        if not token:
            raise InvalidTokenException()
        token = token.split()
        if len(token) != 2:
            raise InvalidTokenException()
        return await token_manager.verify_user_token(token[1])
