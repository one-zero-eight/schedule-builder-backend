__all__ = ["VerifiedDep"]

import time
from typing import Annotated

from authlib.jose import JoseError, JWTClaims, jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.api.exceptions import IncorrectCredentialsException
from src.modules.innohassle_accounts import innohassle_accounts

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Token from [InNoHassle Accounts](https://api.innohassle.ru/accounts/v0/tokens/generate-my-token)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


class UserTokenData(BaseModel):
    innohassle_id: str
    email: str


async def verify_user(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserTokenData:
    token = bearer and bearer.credentials
    if not token:
        raise IncorrectCredentialsException(no_credentials=True)

    token_data = await TokenRepository.verify_user_token(token, IncorrectCredentialsException())
    return token_data

VerifiedDep = Annotated[UserTokenData, Depends(verify_user)]

class TokenRepository:
    _cache = {}

    @classmethod
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        pub_key = innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    @classmethod
    async def verify_user_token(cls, token: str, credentials_exception) -> UserTokenData:
        try:
            payload = cls.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                raise credentials_exception

            # Check cache
            if innohassle_id in cls._cache:
                cached_data = cls._cache[innohassle_id]
                if cached_data["expires_at"] > time.time():
                    return cached_data["user_data"]
                else:
                    del cls._cache[innohassle_id]  # Remove expired cache entry

            # Fetch from DB if not in cache
            innohassle_user = await innohassle_accounts.get_user_by_id(innohassle_id)
            if innohassle_user is None:
                raise credentials_exception

            user_data = UserTokenData(innohassle_id=innohassle_id, email=innohassle_user.innopolis_sso.email)

            # Store in cache with an expiry
            cls._cache[innohassle_id] = {
                "user_data": user_data,
                "expires_at": time.time() + 60 * 60,  # 1 hour
            }

            return user_data
        except JoseError:
            raise credentials_exception
