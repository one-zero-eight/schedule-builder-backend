from datetime import time

import pytest

from src.domain.dtos.lesson import (
    LessonWithCollisionTypeDTO,
    LessonWithExcelCellsDTO,
)
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)


@pytest.mark.parametrize(
    "data, valid_answer",
    [
        # 107 room = Lesson 1 x Lesson 2
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 1",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        teacher="Teacher 1",
                        group_name=["Other 1"],
                        students_number=20,
                        excel_range="F13:G13",
                        collision_type="room",
                        outlook_info=None,
                        date_on=None,
                        date_except=None
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 2",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        teacher="Teacher 2",
                        group_name=["Other 2"],
                        students_number=20,
                        excel_range="B13:E13",
                        collision_type="room",
                        outlook_info=None,
                        date_on=None,
                        date_except=None
                    ),
                ],
            ],
        ),
        # 107 room = Lesson 1 x Lesson 2 x Lesson 3
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 3",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 3",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 1",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        teacher="Teacher 1",
                        group_name=["Other 1"],
                        students_number=20,
                        excel_range="F13:G13",
                        collision_type="room",
                        outlook_info=None,
                        date_on=None,
                        date_except=None
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 2",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        teacher="Teacher 2",
                        group_name=["Other 2"],
                        students_number=20,
                        excel_range="B13:E13",
                        collision_type="room",
                        outlook_info=None,
                        date_on=None,
                        date_except=None
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 3",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        teacher="Teacher 3",
                        group_name=["Other 2"],
                        students_number=20,
                        excel_range="B13:E13",
                        collision_type="room",
                        outlook_info=None,
                        date_on=None,
                        date_except=None
                    ),
                ],
            ],
        ),
        # 107 room = Lesson 1 x Lesson 2
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="107",
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [],
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="107",
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:30:00",
                    end_time="18:55:00",
                    room="108",
                    teacher="Teacher 1",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [],
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="107",
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="18:50:00",
                    end_time="19:30:00",
                    room="108",
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [],
        ),
    ],
)
def test_room_collisions(
    collisions_checker: ICollisionsChecker,
    data: list[LessonWithExcelCellsDTO],
    valid_answer: list[LessonWithCollisionTypeDTO],
) -> None:
    collisions = collisions_checker.get_collisions_by_room(data)
    assert collisions == valid_answer


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
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="b",
                    weekday="MONDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="c",
                    weekday="MONDAY",
                    start_time=time(1, 25, 0),
                    end_time=time(2, 10, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
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
                    date_on=None,
                    date_except=None
                ),
            ],
            0,
        ),
    ],
)
def test_teacher_collisions(
    collisions_checker: ICollisionsChecker,
    timeslots: LessonWithExcelCellsDTO,
    expected: int,
) -> None:
    collisions = collisions_checker.get_collisions_by_teacher(timeslots)
    assert len(collisions) == expected


@pytest.mark.parametrize(
    "data, valid_answer",
    [
        # 70 students in 312
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="312",
                    teacher="Teacher 1",
                    group_name=["Other 1", "Other 2"],
                    students_number=70,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="312",
                    teacher="Teacher 2",
                    group_name=["Other 3", "Other 4"],
                    students_number=70,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 1",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="312",
                        teacher="Teacher 1",
                        group_name=["Other 1", "Other 2"],
                        students_number=70,
                        excel_range="F13:G13",
                        collision_type="capacity",
                        outlook_info=None,
                        room_capacity=30,
                        date_on=None,
                        date_except=None
                    ),
                ],
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 2",
                        weekday="MONDAY",
                        start_time="17:20:00",
                        end_time="18:50:00",
                        room="312",
                        teacher="Teacher 2",
                        group_name=["Other 3", "Other 4"],
                        students_number=70,
                        excel_range="B13:E13",
                        collision_type="capacity",
                        outlook_info=None,
                        room_capacity=30,
                        date_on=None,
                        date_except=None
                    ),
                ],
            ],
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="108",
                    teacher="Teacher 1",
                    group_name=["Other 1", "Other 2"],
                    students_number=70,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="108",
                    teacher="Teacher 2",
                    group_name=["Other 3", "Other 4"],
                    students_number=70,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [],
        ),
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="108",
                    teacher="Teacher 1",
                    group_name=["Other 1", "Other 2"],
                    students_number=200,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="312",
                    teacher="Teacher 2",
                    group_name=["Other 3", "Other 4"],
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None
                ),
            ],
            [],
        ),
    ],
)
def test_space_collisions(
    collisions_checker: ICollisionsChecker,
    data: list[LessonWithExcelCellsDTO],
    valid_answer: list[LessonWithCollisionTypeDTO],
) -> None:
    collisions = (
        collisions_checker.get_lessons_where_not_enough_place_for_students(
            data
        )
    )
    assert collisions == valid_answer
