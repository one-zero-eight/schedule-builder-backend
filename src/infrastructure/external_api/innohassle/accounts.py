import aiohttp
from authlib.jose import JsonWebKey, KeySet

from src.application.external_api.innohassle.interfaces.accounts import (
    IInNoHassleAccounts,
)
from src.domain.dtos.users import UserDTO
from src.domain.exceptions.base import AppException
from typing import AsyncIterable


class InNoHassleAccounts(IInNoHassleAccounts):
    api_url: str
    api_jwt_token: str
    PUBLIC_KID = "public"
    key_set: KeySet

    def __init__(self, api_url: str, api_jwt_token: str):
        self.api_url = api_url
        self.api_jwt_token = api_jwt_token

    async def update_key_set(self):
        self.key_set = await self.get_key_set()

    def get_public_key(self) -> JsonWebKey:
        return self.key_set.find_by_kid(self.PUBLIC_KID)

    async def get_key_set(self) -> KeySet:
        async with aiohttp.ClientSession() as client:
            async with client.get(
                f"{self.api_url}/.well-known/jwks.json"
            ) as response:
                if response.status != 200:
                    raise AppException(status_code=response.status)
                jwks_json = await response.json()
                return JsonWebKey.import_key_set(jwks_json)

    async def get_authorized_client(self) -> AsyncIterable[aiohttp.ClientSession]:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_jwt_token}"},
            base_url=self.api_url,
        ) as client:
            yield client

    async def get_user_by_id(self, innohassle_id: str) -> UserDTO | None:
        async for client in self.get_authorized_client():
            async with client.get(f"users/by-id/{innohassle_id}") as response:
                if response.status != 200:
                    if response.status == 404:
                        return None
                    raise AppException(status_code=response.status, detail=response.reason)
                return UserDTO.model_validate(await response.json())

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        async for client in self.get_authorized_client():
            async with client.get(f"users/by-innomail/{email}") as response:
                if response.status != 200:
                    if response.status == 404:
                        return None
                    raise AppException(status_code=response.status, detail=response.reason)
                return UserDTO.model_validate(await response.json())
