import aiohttp
from authlib.jose import JsonWebKey, KeySet

from src.application.external_api.innohassle.interfaces.accounts import (
    IInNoHassleAccounts,
)
from src.domain.exceptions.base import AppException


class InNoHassleAccounts(IInNoHassleAccounts):
    api_url: str
    api_jwt_token: str
    PUBLIC_KID = "public"
    key_set: KeySet

    def __init__(self, api_url: str):
        self.api_url = api_url

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
