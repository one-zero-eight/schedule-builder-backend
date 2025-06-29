import pytest
from httpx import AsyncClient
from src.domain.dtos.lesson import LessonWithCollisionTypeDTO
import datetime


@pytest.mark.parametrize(
    "spreadsheet_id, expected_result",
    [
        # (
        #     "1amQqvE0rfU92pfMsMnUKA-lTGjlcJ-Sv5UcPpGnxW4w",
        #     [],
        # ),
        (
            "1UazTyY3dXiwN7JWN_6OkjDWTI1-v4W1fZ8WMZJn-CO4",
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Other",
                        weekday="TUESDAY",
                        start_time=datetime.time(9, 0, 0),
                        end_time=datetime.time(10, 30, 0),
                        room="306",
                        teacher="Nursultan Askarbekuly",
                        group_name=[
                            "B24-CSE-01",
                            "B24-CSE-02",
                            "B24-CSE-03",
                            "B24-CSE-04",
                            "B24-CSE-05",
                            "B24-CSE-06",
                            "B24-CSE-07",
                            "B24-DSAI-01",
                            "B24-DSAI-02",
                            "B24-DSAI-03",
                            "B24-DSAI-04",
                            "B24-DSAI-05",
                        ],
                        students_number=345,
                        excel_range="H26:S26",
                        collision_type="capacity",
                        room_capacity=25,
                    )
                ]
            ],
        ),
        (
            "1WcienQ47WiNJVLxO5IpWIN_65OdFKCsgF20E7PBl11M",
            [],
        ),
        (
            "1qJt5prumR2hpuEMGcBmL8GNCO8UN77civ6u8mkgUCfM",
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Software Project (lab)",
                        weekday="MONDAY",
                        start_time=datetime.time(14, 20, 0),
                        end_time=datetime.time(15, 50, 0),
                        room="460",
                        teacher="Marko Pezer",
                        group_name="B24-CSE-03",
                        students_number=29,
                        excel_range="J13",
                        collision_type="room",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Software Project (lab)",
                        weekday="MONDAY",
                        start_time=datetime.time(14, 20, 0),
                        end_time=datetime.time(15, 50, 0),
                        room="460",
                        teacher="Mahmoud Naderi",
                        group_name="B24-CSE-06",
                        students_number=29,
                        excel_range="M13",
                        collision_type="room",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                ]
            ],
        ),
        (
            "133gQ1wdCbq8vuC49NXuz4-tY0SKNZR9lEF9sguXaPnQ",
            [
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Elective course on Physical Education",
                        weekday="WEDNESDAY",
                        start_time=datetime.time(14, 20, 0),
                        end_time=datetime.time(15, 50, 0),
                        room="Elective course on Physical Education",
                        teacher="Elective course on Physical Education",
                        group_name=[
                            "B24-CSE-01",
                            "B24-CSE-02",
                            "B24-CSE-03",
                            "B24-CSE-04",
                            "B24-CSE-05",
                            "B24-CSE-06",
                            "B24-CSE-07",
                            "B24-DSAI-01",
                            "B24-DSAI-02",
                            "B24-DSAI-03",
                            "B24-DSAI-04",
                            "B24-DSAI-05",
                        ],
                        students_number=345,
                        excel_range="H54:S54",
                        collision_type="teacher",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Elective course on Physical Education",
                        weekday="WEDNESDAY",
                        start_time=datetime.time(14, 20, 0),
                        end_time=datetime.time(15, 50, 0),
                        room="Elective course on Physical Education",
                        teacher="Elective course on Physical Education",
                        group_name=[
                            "B23-SD-01",
                            "B23-SD-02",
                            "B23-SD-03",
                            "B23-CBS-01",
                            "B23-CBS-02",
                            "B23-DS-01",
                            "B23-DS-02",
                            "B23-AI-01",
                            "B23-AI-02",
                            "B23-GD-01",
                            "B23-RO-01",
                        ],
                        students_number=290,
                        excel_range="U54:AE54",
                        collision_type="teacher",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                ],
                [
                    LessonWithCollisionTypeDTO(
                        lesson_name="Elective course on Physical Education",
                        weekday="WEDNESDAY",
                        start_time=datetime.time(16, 0, 0),
                        end_time=datetime.time(17, 30, 0),
                        room="Elective course on Physical Education",
                        teacher="Elective course on Physical Education",
                        group_name=[
                            "B24-CSE-01",
                            "B24-CSE-02",
                            "B24-CSE-03",
                            "B24-CSE-04",
                            "B24-CSE-05",
                            "B24-CSE-06",
                            "B24-CSE-07",
                            "B24-DSAI-01",
                            "B24-DSAI-02",
                            "B24-DSAI-03",
                            "B24-DSAI-04",
                            "B24-DSAI-05",
                        ],
                        students_number=345,
                        excel_range="H57:S57",
                        collision_type="teacher",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                    LessonWithCollisionTypeDTO(
                        lesson_name="Elective course on Physical Education",
                        weekday="WEDNESDAY",
                        start_time=datetime.time(16, 0, 0),
                        end_time=datetime.time(17, 30, 0),
                        room="Elective course on Physical Education",
                        teacher="Elective course on Physical Education",
                        group_name=[
                            "B23-SD-01",
                            "B23-SD-02",
                            "B23-SD-03",
                            "B23-CBS-01",
                            "B23-CBS-02",
                            "B23-DS-01",
                            "B23-DS-02",
                            "B23-AI-01",
                            "B23-AI-02",
                            "B23-GD-01",
                            "B23-RO-01",
                        ],
                        students_number=290,
                        excel_range="U57:AE57",
                        collision_type="teacher",
                        outlook_info=None,
                        room_capacity=None,
                    ),
                ],
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_check_excel_collisions(
    fastapi_test_client: AsyncClient,
    spreadsheet_id: str,
    expected_result: list[list[LessonWithCollisionTypeDTO]],
) -> None:
    response = await fastapi_test_client.get(
        url="/collisions/check",
        params={"google_spreadsheet_id": spreadsheet_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected_result
