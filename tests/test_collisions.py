from datetime import time

import pytest
import yaml

from src.modules.bookings.client import RoomDTO
from src.modules.collisions.collision_checker import CollisionChecker
from src.modules.collisions.schemas import CapacityIssue, RoomIssue, TeacherIssue
from src.modules.parsers.schemas import LessonWithExcelCellsDTO

rooms_yaml = """
rooms:
  # Yellow Access Rooms (for students) >
  - id: "301"
    title: "Lecture Room 301"
    short_name: "301"
    access_level: "yellow"
    capacity: 24
    restrict_daytime: true

  - id: "303"
    title: "Lecture Room 303"
    short_name: "303"
    access_level: "yellow"
    capacity: 30
    restrict_daytime: true

  - id: "304"
    title: "Lecture Room 304"
    short_name: "304"
    access_level: "yellow"
    capacity: 25
    restrict_daytime: true

  - id: "305"
    title: "Lecture Room 305"
    short_name: "305"
    access_level: "yellow"
    capacity: 25
    restrict_daytime: true

  - id: "312"
    title: "Lecture Room 312"
    short_name: "312"
    access_level: "yellow"
    capacity: 30
    restrict_daytime: true

  - id: "313"
    title: "Lecture Room 313"
    short_name: "313"
    access_level: "yellow"
    capacity: 60
    restrict_daytime: true

  - id: "314"
    title: "Lecture Room 314"
    short_name: "314"
    access_level: "yellow"
    capacity: 34
    restrict_daytime: true

  - id: "318"
    title: "Lecture Room 318"
    short_name: "318"
    access_level: "yellow"
    capacity: 30
    restrict_daytime: true

  - id: "320"
    title: "Lecture Room 320"
    short_name: "320"
    access_level: "yellow"
    capacity: 28
    restrict_daytime: true
  # Yellow Access Rooms (for students) <

  - id: "309A"
    title: "Clubs Room 309A"
    short_name: "309A"
    access_level: "special"

  # Red Access Rooms (lecture rooms) >

  - id: "101"
    short_name: "101"
    title: "Lecture Room 101"
    access_level: "red"
    capacity: 32

  - id: "102"
    short_name: "102"
    title: "Lecture Room 102"
    access_level: "red"
    capacity: 18

  - id: "103"
    short_name: "103"
    title: "Lecture Room 103"
    access_level: "red"
    capacity: 21

  - id: "104"
    short_name: "104"
    title: "Lecture Room 104"
    access_level: "red"
    capacity: 20

  - id: "105"
    short_name: "105 (West)"
    title: "Lecture Room 105 (West)"
    access_level: "red"
    capacity: 240

  - id: "106"
    short_name: "106 (South)"
    title: "Lecture Room 106 (South)"
    access_level: "red"
    capacity: 140

  - id: "107"
    short_name: "107 (North)"
    title: "Lecture Room 107 (North)"
    access_level: "red"
    capacity: 150

  - id: "108"
    short_name: "108 (East)"
    title: "Lecture Room 108 (East)"
    access_level: "red"
    capacity: 288

  - id: "300"
    short_name: "300"
    title: "Lecture Room 300"
    access_level: "red"
    capacity: 48

  - id: "306"
    short_name: "306"
    title: "Lecture Room 306"
    access_level: "red"
    capacity: 18

  - id: "307"
    short_name: "307"
    title: "Lecture Room 307"
    access_level: "red"
    capacity: 60

  - id: "308"
    short_name: "308"
    title: "Lecture Room 308"
    access_level: "red"
    capacity: 35

  - id: "316"
    short_name: "316"
    title: "Lecture Room 316"
    access_level: "red"
    capacity: 26

  - id: "317"
    short_name: "317"
    title: "Lecture Room 317"
    access_level: "red"
    capacity: 26

  - id: "321"
    short_name: "321"
    title: "Lecture Room 321"
    access_level: "red"
    capacity: 48

  - id: "421"
    short_name: "421"
    title: "Lecture Room 421"
    access_level: "red"
    capacity: 30

  - id: "425"
    short_name: "425"
    title: "Big Meeting Room 425"
    access_level: "red"
    capacity: 30

  - id: "452"
    short_name: "452"
    title: "Lecture Room 452"
    access_level: "red"
    capacity: 16

  - id: "460"
    short_name: "460"
    title: "Lecture Room 460"
    access_level: "red"
    capacity: 30

  - id: "461"
    short_name: "461"
    title: "Lecture Room 461"
    access_level: "red"
    capacity: 30
  # Red Access Rooms (lecture rooms) <
"""

rooms = yaml.safe_load(rooms_yaml)["rooms"]


@pytest.fixture
def collisions_checker() -> CollisionChecker:
    return CollisionChecker(
        token="test_token",
        teachers=[],
        rooms=[RoomDTO.model_validate(room) for room in rooms],
    )


@pytest.mark.parametrize(
    "data, expected_issues",
    [
        # Test case: Two lessons in same room at same time
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 1",
                    group_name=("Group 1",),
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None,
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 2",
                    group_name=("Group 2",),
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expected number of room issues
        ),
        # Test case: No room collision - different times
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time=time(17, 20),
                    end_time=time(18, 50),
                    room="107",
                    teacher="Teacher 1",
                    group_name=("Group 1",),
                    students_number=20,
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None,
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 2",
                    group_name=("Group 2",),
                    students_number=20,
                    excel_range="B13:E13",
                    date_on=None,
                    date_except=None,
                ),
            ],
            0,  # No room collision expected
        ),
    ],
)
def test_room_collisions(
    collisions_checker: CollisionChecker,
    data: list[LessonWithExcelCellsDTO],
    expected_issues: int,
) -> None:
    issues = collisions_checker.check_for_room_issue(data)
    assert len(issues) == expected_issues

    if expected_issues > 0:
        issue = issues[0]
        assert isinstance(issue, RoomIssue)
        assert issue.collision_type == "room"
        assert len(issue.lessons) >= 2  # Should have at least 2 conflicting lessons


@pytest.mark.parametrize(
    "timeslots, expected_issues",
    [
        # Test case: Same teacher, overlapping times
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson A",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                    date_on=None,
                    date_except=None,
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson B",
                    weekday="MONDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="319",
                    teacher="Ivan",
                    group_name="DSE",
                    students_number=20,
                    excel_range="B1:B1",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expect teacher collision
        ),
        # Test case: Same teacher, different days
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson A",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                    date_on=None,
                    date_except=None,
                ),
                LessonWithExcelCellsDTO(
                    lesson_name="Lesson B",
                    weekday="TUESDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    excel_range="A1:A1",
                    date_on=None,
                    date_except=None,
                ),
            ],
            0,  # No collision - different days
        ),
    ],
)
def test_teacher_collisions(
    collisions_checker: CollisionChecker,
    timeslots: list[LessonWithExcelCellsDTO],
    expected_issues: int,
) -> None:
    issues = collisions_checker.check_for_teacher_issue(timeslots)
    assert len(issues) == expected_issues

    if expected_issues > 0:
        issue = issues[0]
        assert isinstance(issue, TeacherIssue)
        assert issue.collision_type == "teacher"


@pytest.mark.parametrize(
    "data, expected_issues",
    [
        # Test case: Too many students for room capacity
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Large Lesson",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="312",  # Room 312 has capacity 30
                    teacher="Teacher 1",
                    group_name=("Group A", "Group B"),
                    students_number=70,  # Exceeds capacity
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expect capacity issue
        ),
        # Test case: Students fit in room
        (
            [
                LessonWithExcelCellsDTO(
                    lesson_name="Small Lesson",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="312",  # Room 312 has capacity 30
                    teacher="Teacher 1",
                    group_name=("Group A",),
                    students_number=20,  # Within capacity
                    excel_range="F13:G13",
                    date_on=None,
                    date_except=None,
                ),
            ],
            0,  # No capacity issue
        ),
    ],
)
def test_capacity_collisions(
    collisions_checker: CollisionChecker,
    data: list[LessonWithExcelCellsDTO],
    expected_issues: int,
) -> None:
    issues = collisions_checker.check_for_capacity_issue(data)
    assert len(issues) == expected_issues

    if expected_issues > 0:
        issue = issues[0]
        assert isinstance(issue, CapacityIssue)
        assert issue.collision_type == "capacity"
        assert issue.needed_capacity > (issue.room_capacity or 0)
