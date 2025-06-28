import pytest
import pytest_asyncio

from src.domain.dtos.lesson import LessonWithExcelCellsDTO
from src.domain.dtos.lesson import LessonWithCollisionTypeDTO
from src.application.use_cases.collisions import CollisionsChecker

@pytest.mark.parametrize(
        "data, valid_answer",
        [
            # 107 room = Lesson 1 x Lesson 2
            (
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    room_capacity=None,
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13"
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    room_capacity=None,
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13"
                )
            ),
            (
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 1",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        room_capacity=None,
                        teacher="Teacher 1",
                        group_name=["Other 1"],
                        students_number=20,
                        excel_range="F13:G13",
                        collision_type="room",
                        outlook_info=None
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 2",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="107",
                        room_capacity=None,
                        teacher="Teacher 2",
                        group_name=["Other 2"],
                        students_number=20,
                        excel_range="B13:E13",
                        collision_type="room",
                        outlook_info=None
                    )
                ]
            )
        ],
        [
            # 107 room = Lesson 1 x Lesson 2
            (
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="107",
                    room_capacity=None,
                    teacher="Teacher 1",
                    group_name=["Other 1"],
                    students_number=20,
                    excel_range="F13:G13"
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="107",
                    room_capacity=None,
                    teacher="Teacher 2",
                    group_name=["Other 2"],
                    students_number=20,
                    excel_range="B13:E13"
                )
            ),
            (
                [
                ]
            )
        ]
)
@pytest.mark.asyncio
async def test_room_collisions(
    collisions_checker: CollisionsChecker,
    data: list[LessonWithExcelCellsDTO]
) -> None:
    pass

@pytest.mark.asyncio
async def test_teacher_collisions(
    teacher_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass

@pytest.mark.parametrize(
        "data, valid_answer",
        [
            # 70 students in 312
            (
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="312",
                    room_capacity=None,
                    teacher="Teacher 1",
                    group_name=["Other 1", "Other 2"],
                    students_number=70,
                    excel_range="F13:G13"
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="312",
                    room_capacity=None,
                    teacher="Teacher 2",
                    group_name=["Other 3", "Other 4"],
                    students_number=70,
                    excel_range="B13:E13"
                )
            ),
            (
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Lesson 1",
                        weekday="MONDAY",
                        start_time="14:20:00",
                        end_time="15:50:00",
                        room="312",
                        room_capacity=None,
                        teacher="Teacher 1",
                        group_name=["Other 1", "Other 2"],
                        students_number=70,
                        excel_range="B13:E13",  
                        collision_type="room",
                        outlook_info=None
                    ),
                    LessonWithCollisionTypeDTO(
                    lesson_name="Lesson 2",
                        weekday="MONDAY",
                        start_time="17:20:00",
                        end_time="18:50:00",
                        room="312",
                        room_capacity=None,
                        teacher="Teacher 2",
                        group_name=["Other 3", "Other 4"],
                        students_number=70,
                        excel_range="B13:E13",
                        collision_type="room",
                        outlook_info=None
                    )
                ]
            )
        ],
        [
            (
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time="14:20:00",
                    end_time="15:50:00",
                    room="108",
                    room_capacity=None,
                    teacher="Teacher 1",
                    group_name=["Other 1", "Other 2"],
                    students_number=70,
                    excel_range="F13:G13"
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time="17:20:00",
                    end_time="18:50:00",
                    room="108",
                    room_capacity=None,
                    teacher="Teacher 2",
                    group_name=["Other 3", "Other 4"],
                    students_number=70,
                    excel_range="B13:E13"
                )
            ),
            (
                [
                ]
            )
        ]
)
@pytest.mark.asyncio
async def test_space_collisions(
    space_collisions: LessonWithExcelCellsDTO,
) -> None:
    pass