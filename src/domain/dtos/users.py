import datetime

from pydantic import BaseModel


class UserTokenDataDTO(BaseModel):
    innohassle_id: str
    email: str | None = None


class UserInfoFromSSODTO(BaseModel):
    email: str
    name: str | None
    issued_at: datetime.datetime | None


class UserDTO(BaseModel):
    innopolis_sso: UserInfoFromSSODTO | None
