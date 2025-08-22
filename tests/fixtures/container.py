from collections.abc import AsyncIterable

import pytest_asyncio
from dishka import AsyncContainer, make_async_container

from src.infrastructure.services.collisions_checker import CollisionsChecker
from src.presentation.dependencies.rooms import RoomsWithCapacityProvider
from src.presentation.dependencies.services.collisions_checker import (
    CollisionsCheckerProvider,
)
from src.presentation.dependencies.services.graph import GraphProvider
from src.presentation.dependencies.teacher import TeachersProvider
from tests.mocks.booking import MockBookingServiceProvider


@pytest_asyncio.fixture
async def container() -> AsyncIterable[AsyncContainer]:
    container = make_async_container(
        MockBookingServiceProvider(),
        TeachersProvider(),
        CollisionsCheckerProvider(),
        RoomsWithCapacityProvider(),
        GraphProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def collisions_checker(container: AsyncContainer) -> CollisionsChecker:
    async with container() as request_container:
        return await request_container.get(CollisionsChecker)
