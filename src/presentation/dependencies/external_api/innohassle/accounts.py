from dishka import Provider, Scope, provide

from src.application.external_api.innohassle.interfaces.accounts import (
    IInNoHassleAccounts,
)
from src.config import settings
from src.infrastructure.external_api.innohassle.accounts import (
    InNoHassleAccounts,
)


class InNoHassleAccountsProvider(Provider):
    scope = Scope.APP

    @provide
    def get_innohassle_accounts(self) -> IInNoHassleAccounts:
        return InNoHassleAccounts(
            api_url=settings.accounts.api_url,
            api_jwt_token=settings.accounts.api_jwt_token.get_secret_value(),
        )
