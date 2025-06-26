import pytest
import pytest_asyncio

from src.domain.dtos.lesson import LessonWithExcelCellsDTO


@pytest_asyncio.fixture
async def outlook_collisions() -> LessonWithExcelCellsDTO:
    pass


@pytest_asyncio.fixture
async def room_collisions() -> LessonWithExcelCellsDTO:
    return {"s": 1}


@pytest_asyncio.fixture
async def sort_collisions() -> LessonWithExcelCellsDTO:
    pass


@pytest_asyncio.fixture
async def space_collisions() -> LessonWithExcelCellsDTO:
    pass


@pytest_asyncio.fixture
async def teacher_collisions() -> LessonWithExcelCellsDTO:
    pass
