import time

from authlib.jose import JoseError, JWTClaims, jwt

from application.external_api.innohassle.interfaces.token_manager import (
    ITokenManager,
)
from src.application.external_api.innohassle.interfaces.accounts import (
    IInNoHassleAccounts,
)
from src.domain.dtos.users import UserTokenDataDTO
from src.domain.exceptions.tokens import InvalidTokenException


class TokenManager(ITokenManager):
    _cache = {}

    def __init__(self, innohassle_accounts: IInNoHassleAccounts) -> None:
        self.innohassle_accounts = innohassle_accounts

    def decode_token(self, token: str) -> JWTClaims:
        now = time.time()
        pub_key = self.innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    async def verify_user_token(self, token: str) -> UserTokenDataDTO:
        credentials_exception = InvalidTokenException()
        try:
            payload = self.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                raise credentials_exception

            # Check cache
            if innohassle_id in self.__class__._cache:
                cached_data = self.__class__._cache[innohassle_id]
                if cached_data["expires_at"] > time.time():
                    return cached_data["user_data"]
                else:
                    del self.__class__._cache[
                        innohassle_id
                    ]  # Remove expired cache entry

            # Fetch from DB if not in cache
            innohassle_user = await self.innohassle_accounts.get_user_by_id(
                innohassle_id
            )
            if innohassle_user is None:
                raise credentials_exception

            user_data = UserTokenDataDTO(
                innohassle_id=innohassle_id,
                email=innohassle_user.innopolis_sso.email,
            )

            # Store in cache with an expiry
            self.__class__._cache[innohassle_id] = {
                "user_data": user_data,
                "expires_at": time.time() + 60 * 60,  # 1 hour
            }

            return user_data
        except JoseError:
            raise credentials_exception
