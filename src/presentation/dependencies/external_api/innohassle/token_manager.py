from dishka import Provider, Scope, provide

from src.infrastructure.external_api.innohassle.accounts import InNoHassleAccounts
from src.infrastructure.external_api.innohassle.token_manager import (
    TokenManager,
)


class TokenManagerProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_token_manager(
        self, accounts: InNoHassleAccounts
    ) -> TokenManager:
        return TokenManager(accounts)
