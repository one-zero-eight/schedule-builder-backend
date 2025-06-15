from dishka import Provider, Scope, provide

from application.external_api.innohassle.interfaces.token_manager import (
    ITokenManager,
)
from src.application.external_api.innohassle.interfaces.accounts import (
    IInNoHassleAccounts,
)
from src.infrastructure.external_api.innohassle.token_manager import (
    TokenManager,
)


class TokenManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_token_manager(
        self, accounts: IInNoHassleAccounts
    ) -> ITokenManager:
        return TokenManager(accounts)
