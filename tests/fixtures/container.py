import pytest_asyncio

from src.modules.collisions.collision_checker import CollisionChecker, collision_checker


@pytest_asyncio.fixture
async def collisions_checker() -> CollisionChecker:
    return collision_checker
