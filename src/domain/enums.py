from enum import Enum


class CollisionTypeEnum(Enum):
    ROOM = "room"
    TEACHER = "teacher"
    CAPACITY = "capacity"
    OUTLOOK = "outlook"


class Weekdays(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class CourseTypeEnum(Enum):
    CORE = "core"
    ELECTIVE = "elective"
