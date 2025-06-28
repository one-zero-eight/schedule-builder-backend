from datetime import time

import pytest

from src.domain.dtos.lesson import (
    LessonWithExcelCellsDTO,
)
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)


@pytest.mark.asyncio
async def test_room_collisions(
    room_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass


@pytest.mark.parametrize(
    "timeslots, expected",
    [
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="MONDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
            ],
            1,
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="TUESDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
            ],
            0,
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="a",
                    weekday="MONDAY",
                    start_time=time(3, 30, 0),
                    end_time=time(5, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                ),
            ],
            0,
        ),
    ],
)
@pytest.mark.asyncio
async def test_teacher_collisions(
    collisions_checker: ICollisionsChecker,
    timeslots: LessonWithExcelCellsDTO,
    expected: int,
) -> None:
    collisions = await collisions_checker.get_collisions_by_teacher(timeslots)
    assert len(collisions) == expected


@pytest.mark.asyncio
async def test_space_collisions(
    space_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass
