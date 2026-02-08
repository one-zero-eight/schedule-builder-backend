from datetime import date, time

import pytest
import yaml

from src.modules.bookings.client import RoomDTO
from src.modules.collisions.collision_checker import CollisionChecker
from src.modules.collisions.schemas import CapacityIssue, Lesson, RoomIssue, TeacherIssue
from src.modules.options.repository import Teacher

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
                Lesson(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 1",
                    group_name=("Group 1",),
                    students_number=20,
                    a1_range="F13:G13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
                Lesson(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 2",
                    group_name=("Group 2",),
                    students_number=20,
                    a1_range="B13:E13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expected number of room issues
        ),
        # Test case: No room collision - different times
        (
            [
                Lesson(
                    lesson_name="Lesson 1",
                    weekday="MONDAY",
                    start_time=time(17, 20),
                    end_time=time(18, 50),
                    room="107",
                    teacher="Teacher 1",
                    group_name=("Group 1",),
                    students_number=20,
                    a1_range="F13:G13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
                Lesson(
                    lesson_name="Lesson 2",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="107",
                    teacher="Teacher 2",
                    group_name=("Group 2",),
                    students_number=20,
                    a1_range="B13:E13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
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
    data: list[Lesson],
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
                Lesson(
                    lesson_name="Lesson A",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    a1_range="A1:A1",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
                Lesson(
                    lesson_name="Lesson B",
                    weekday="MONDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="319",
                    teacher="Ivan",
                    group_name="DSE",
                    students_number=20,
                    a1_range="B1:B1",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expect teacher collision
        ),
        # Test case: Same teacher, different days
        (
            [
                Lesson(
                    lesson_name="Lesson A",
                    weekday="MONDAY",
                    start_time=time(1, 0, 0),
                    end_time=time(2, 0, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    a1_range="A1:A1",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
                Lesson(
                    lesson_name="Lesson B",
                    weekday="TUESDAY",
                    start_time=time(1, 30, 0),
                    end_time=time(2, 30, 0),
                    room="318",
                    teacher="Ivan",
                    group_name="CSE",
                    students_number=20,
                    a1_range="A1:A1",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
            ],
            0,  # No collision - different days
        ),
        # ONLY ON: same lesson, main (weekday + date_except) + nested (date_on) — no teacher conflict
        (
            [
                Lesson(
                    lesson_name="Основы и методология программирования",
                    weekday="THURSDAY",
                    start_time=time(17, 40),
                    end_time=time(19, 10),
                    room="321",
                    teacher="Егор Дмитриев",
                    group_name="B25-AI360-01",
                    students_number=30,
                    a1_range="A1:A1",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=[date(2025, 1, 23), date(2025, 1, 30)],
                ),
                Lesson(
                    lesson_name="Основы и методология программирования",
                    weekday="THURSDAY",
                    start_time=time(17, 40),
                    end_time=time(19, 10),
                    room="307",
                    teacher="Егор Дмитриев",
                    group_name="B25-AI360-01",
                    students_number=30,
                    a1_range="A2:A2",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=[date(2025, 1, 23), date(2025, 1, 30)],
                    date_except=None,
                ),
            ],
            0,  # No collision — ONLY ON: nested dates are in main's date_except
        ),
    ],
)
def test_teacher_collisions(
    collisions_checker: CollisionChecker,
    timeslots: list[Lesson],
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
                Lesson(
                    lesson_name="Large Lesson",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="312",  # Room 312 has capacity 30
                    teacher="Teacher 1",
                    group_name=("Group A", "Group B"),
                    students_number=70,  # Exceeds capacity
                    a1_range="F13:G13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
                    date_on=None,
                    date_except=None,
                ),
            ],
            1,  # Expect capacity issue
        ),
        # Test case: Students fit in room
        (
            [
                Lesson(
                    lesson_name="Small Lesson",
                    weekday="MONDAY",
                    start_time=time(14, 20),
                    end_time=time(15, 50),
                    room="312",  # Room 312 has capacity 30
                    teacher="Teacher 1",
                    group_name=("Group A",),
                    students_number=20,  # Within capacity
                    a1_range="F13:G13",
                    spreadsheet_id="test_spreadsheet",
                    google_sheet_gid="test_gid",
                    google_sheet_name="test_sheet",
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
    data: list[Lesson],
    expected_issues: int,
) -> None:
    issues = collisions_checker.check_for_capacity_issue(data)
    assert len(issues) == expected_issues

    if expected_issues > 0:
        issue = issues[0]
        assert isinstance(issue, CapacityIssue)
        assert issue.collision_type == "capacity"
        assert issue.needed_capacity > (issue.room_capacity or 0)


class TestTeacherStudentCollisions:
    """Tests for teacher-student collision detection (teachers who are also students)."""

    @pytest.fixture
    def checker_with_student_teachers(self) -> CollisionChecker:
        """Checker with teachers who have student_group set."""
        teachers = [
            Teacher(name="Ivan Petrov", russian_name="Иван Петров", student_group="B4-CSE-05"),
            Teacher(name="Anna Smith", student_group="B4-DS-01"),
        ]
        return CollisionChecker(
            token="test_token",
            teachers=teachers,
            rooms=[RoomDTO.model_validate(room) for room in rooms],
        )

    def test_teaching_vs_studying_collision(self, checker_with_student_teachers: CollisionChecker) -> None:
        """Teacher teaches one group while their own group has a lesson at the same time."""
        lessons = [
            Lesson(
                lesson_name="Math",
                weekday="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 30),
                room="301",
                teacher="Ivan Petrov",
                group_name="B4-CSE-01",
                students_number=20,
                a1_range="A1:A1",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
            Lesson(
                lesson_name="Physics",
                weekday="MONDAY",
                start_time=time(10, 30),
                end_time=time(12, 0),
                room="302",
                teacher="Other Teacher",
                group_name="B4-CSE-05",  # Ivan's student group
                students_number=20,
                a1_range="A2:A2",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
        ]
        issues = checker_with_student_teachers.check_for_teacher_issue(lessons)
        assert len(issues) == 1
        issue = issues[0]
        assert issue.teacher == "ivan petrov"
        assert len(issue.teaching_lessons) == 1
        assert len(issue.studying_lessons) == 1
        assert issue.teaching_lessons[0].lesson_name == "Math"
        assert issue.studying_lessons[0].lesson_name == "Physics"

    def test_studying_vs_studying_collision(self, checker_with_student_teachers: CollisionChecker) -> None:
        """Teacher's student group has two lessons at the same time."""
        lessons = [
            Lesson(
                lesson_name="Physics",
                weekday="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 30),
                room="301",
                teacher="Teacher A",
                group_name="B4-CSE-05",  # Ivan's student group
                students_number=20,
                a1_range="A1:A1",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
            Lesson(
                lesson_name="Chemistry",
                weekday="MONDAY",
                start_time=time(10, 30),
                end_time=time(12, 0),
                room="302",
                teacher="Teacher B",
                group_name="B4-CSE-05",  # Same group - Ivan must attend both
                students_number=20,
                a1_range="A2:A2",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
        ]
        issues = checker_with_student_teachers.check_for_teacher_issue(lessons)
        assert len(issues) == 1
        issue = issues[0]
        assert issue.teacher == "ivan petrov"
        assert len(issue.teaching_lessons) == 0
        assert len(issue.studying_lessons) == 2

    def test_no_collision_different_times(self, checker_with_student_teachers: CollisionChecker) -> None:
        """No collision when teaching and studying lessons don't overlap."""
        lessons = [
            Lesson(
                lesson_name="Math",
                weekday="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 30),
                room="301",
                teacher="Ivan Petrov",
                group_name="B4-CSE-01",
                students_number=20,
                a1_range="A1:A1",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
            Lesson(
                lesson_name="Physics",
                weekday="MONDAY",
                start_time=time(14, 0),
                end_time=time(15, 30),
                room="302",
                teacher="Other Teacher",
                group_name="B4-CSE-05",  # Ivan's student group but different time
                students_number=20,
                a1_range="A2:A2",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
        ]
        issues = checker_with_student_teachers.check_for_teacher_issue(lessons)
        assert len(issues) == 0

    def test_teacher_name_case_insensitive(self, checker_with_student_teachers: CollisionChecker) -> None:
        """Teacher name matching should be case insensitive."""
        lessons = [
            Lesson(
                lesson_name="Math",
                weekday="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 30),
                room="301",
                teacher="IVAN PETROV",  # Different case
                group_name="B4-CSE-01",
                students_number=20,
                a1_range="A1:A1",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
            Lesson(
                lesson_name="Physics",
                weekday="MONDAY",
                start_time=time(10, 30),
                end_time=time(12, 0),
                room="302",
                teacher="Other Teacher",
                group_name="B4-CSE-05",
                students_number=20,
                a1_range="A2:A2",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
        ]
        issues = checker_with_student_teachers.check_for_teacher_issue(lessons)
        assert len(issues) == 1

    def test_multiple_groups_in_lesson(self, checker_with_student_teachers: CollisionChecker) -> None:
        """Lesson with multiple groups should detect teacher-student in any group."""
        lessons = [
            Lesson(
                lesson_name="Math",
                weekday="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 30),
                room="301",
                teacher="Ivan Petrov",
                group_name="B4-CSE-01",
                students_number=20,
                a1_range="A1:A1",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
            Lesson(
                lesson_name="Lecture",
                weekday="MONDAY",
                start_time=time(10, 30),
                end_time=time(12, 0),
                room="105",
                teacher="Professor",
                group_name=("B4-CSE-04", "B4-CSE-05", "B4-CSE-06"),  # Ivan's group is in this tuple
                students_number=60,
                a1_range="A2:A2",
                spreadsheet_id="test",
                google_sheet_gid="test",
                google_sheet_name="test",
                date_on=None,
                date_except=None,
            ),
        ]
        issues = checker_with_student_teachers.check_for_teacher_issue(lessons)
        assert len(issues) == 1
        assert issues[0].teacher == "ivan petrov"


def test_start_at_till_same_logical_lesson_no_room_or_teacher_conflict(
    collisions_checker: CollisionChecker,
) -> None:
    """START AT + following TILL same subject/room/teacher with overlapping time = one lesson, no conflict."""
    lessons = [
        Lesson(
            lesson_name="Research seminar",
            weekday="MONDAY",
            start_time=time(17, 0),
            end_time=time(18, 30),
            room="460",
            teacher="Bader Rasheed",
            group_name=("Group 1",),
            students_number=20,
            a1_range="A1:A1",
            spreadsheet_id="test",
            google_sheet_gid="test",
            google_sheet_name="test",
            date_on=None,
            date_except=None,
        ),
        Lesson(
            lesson_name="Research seminar",
            weekday="MONDAY",
            start_time=time(17, 20),
            end_time=time(20, 0),
            room="460",
            teacher="Bader Rasheed",
            group_name=("Group 1",),
            students_number=20,
            a1_range="A2:A2",
            spreadsheet_id="test",
            google_sheet_gid="test",
            google_sheet_name="test",
            date_on=None,
            date_except=None,
        ),
    ]
    room_issues = collisions_checker.check_for_room_issue(lessons)
    teacher_issues = collisions_checker.check_for_teacher_issue(lessons)
    assert len(room_issues) == 0
    assert len(teacher_issues) == 0


def test_start_at_till_cto_toolkit_two_instructors_no_conflict(
    collisions_checker: CollisionChecker,
) -> None:
    """Same subject, same room, same teachers (e.g. CTO Toolkit 301 STARTS AT 15:00 / 301 TILL 16:30) = one lesson."""
    lessons = [
        Lesson(
            lesson_name="CTO Toolkit",
            weekday="TUESDAY",
            start_time=time(15, 0),
            end_time=time(15, 50),
            room="301",
            teacher="Alexey Mustafin / Dmitriy Kamyshnikov",
            group_name=("Group 1",),
            students_number=25,
            a1_range="A1:A1",
            spreadsheet_id="test",
            google_sheet_gid="test",
            google_sheet_name="test",
            date_on=None,
            date_except=None,
        ),
        Lesson(
            lesson_name="CTO Toolkit",
            weekday="TUESDAY",
            start_time=time(15, 30),
            end_time=time(16, 30),
            room="301",
            teacher="Alexey Mustafin / Dmitriy Kamyshnikov",
            group_name=("Group 1",),
            students_number=25,
            a1_range="A2:A2",
            spreadsheet_id="test",
            google_sheet_gid="test",
            google_sheet_name="test",
            date_on=None,
            date_except=None,
        ),
    ]
    room_issues = collisions_checker.check_for_room_issue(lessons)
    teacher_issues = collisions_checker.check_for_teacher_issue(lessons)
    assert len(room_issues) == 0
    assert len(teacher_issues) == 0


class TestOnlyOnTimeCollision:
    """ONLY ON: main lesson (weekday + date_except) and nested (date_on) must not collide by time."""

    def _lesson(
        self,
        *,
        weekday: str = "THURSDAY",
        room: str = "321",
        date_on: list[date] | None = None,
        date_except: list[date] | None = None,
    ) -> Lesson:
        return Lesson(
            lesson_name="Programming",
            weekday=weekday,
            start_time=time(17, 40),
            end_time=time(19, 10),
            room=room,
            teacher="Егор Дмитриев",
            group_name="B25-AI360-01",
            students_number=30,
            a1_range="A1:A1",
            spreadsheet_id="test",
            google_sheet_gid="test",
            google_sheet_name="test",
            date_on=date_on,
            date_except=date_except,
        )

    def test_only_on_main_vs_nested_no_collision(self) -> None:
        """Main (weekday + date_except) vs nested (date_on = those dates) → no collision."""
        only_on_dates = [date(2025, 1, 23), date(2025, 1, 30)]  # Thursdays
        main = self._lesson(room="321", date_except=only_on_dates)
        nested = self._lesson(room="307", date_on=only_on_dates)
        assert CollisionChecker.check_two_timeslots_collisions_by_time(main, nested) is False
        assert CollisionChecker.check_two_timeslots_collisions_by_time(nested, main) is False

    def test_only_on_overlapping_dates_collision(self) -> None:
        """If date_on not fully in date_except, time overlap counts as collision."""
        # 2025-01-23 and 2025-01-30 are Thursdays
        main = self._lesson(room="321", date_except=[date(2025, 1, 23)])
        nested = self._lesson(room="307", date_on=[date(2025, 1, 23), date(2025, 1, 30)])
        assert CollisionChecker.check_two_timeslots_collisions_by_time(main, nested) is True
        assert CollisionChecker.check_two_timeslots_collisions_by_time(nested, main) is True
