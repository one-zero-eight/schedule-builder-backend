import time

from authlib.jose import JoseError, JWTClaims, jwt

from src.domain.dtos.users import UserTokenDataDTO
from src.domain.exceptions.tokens import InvalidTokenException


class TokenManager:
    def __init__(self, innohassle_accounts) -> None:
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
            user_data = UserTokenDataDTO(
                innohassle_id=innohassle_id,
                token=token,
            )
            return user_data
        except JoseError:
            raise credentials_exception
