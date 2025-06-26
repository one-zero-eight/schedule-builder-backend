import pytest
import pytest_asyncio

from src.domain.dtos.lesson import LessonWithExcelCellsDTO


@pytest.mark.asyncio
async def test_room_collisions(
    room_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass


@pytest.mark.asyncio
async def test_teacher_collisions(
    teacher_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass


@pytest.mark.asyncio
async def test_space_collisions(
    space_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass


@pytest.mark.asyncio
async def test_outlook_collisions(
    outlook_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass


@pytest.mark.asyncio
async def test_sort_collisions(
    sort_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass
