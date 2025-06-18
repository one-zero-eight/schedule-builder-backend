from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.presentation.dependencies.external_api.innohassle.accounts import (
    InNoHassleAccountsProvider,
)
from src.presentation.dependencies.external_api.innohassle.booking import (
    BookingServiceProvider,
)
from src.presentation.dependencies.external_api.innohassle.room import (
    RoomServiceProvider,
)
from src.presentation.dependencies.external_api.innohassle.token import (
    UserTokenDataProvider,
)
from src.presentation.dependencies.external_api.innohassle.token_manager import (
    TokenManagerProvider,
)
from src.presentation.dependencies.parsers import CoursesParsersProvider
from src.presentation.dependencies.teacher import TeachersProvider
from src.presentation.dependencies.use_cases.collisions import (
    CollisionsCheckerProvider,
)
from src.presentation.dependencies.rooms import RoomsWithCapacityProvider


def create_async_container() -> AsyncContainer:
    container = make_async_container(
        FastapiProvider(),
        BookingServiceProvider(),
        RoomServiceProvider(),
        InNoHassleAccountsProvider(),
        TokenManagerProvider(),
        UserTokenDataProvider(),
        TeachersProvider(),
        CoursesParsersProvider(),
        CollisionsCheckerProvider(),
        RoomsWithCapacityProvider(),
    )
    return container
