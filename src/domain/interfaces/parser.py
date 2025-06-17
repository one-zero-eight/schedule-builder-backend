from abc import ABC, abstractmethod

# from src.domain.dtos.lesson import LessonWithTeacherAndGroup


class ICoursesParser(ABC):
    @abstractmethod
    def get_all_timeslots(
        self, spreadsheet_id: str
    ):
        pass
