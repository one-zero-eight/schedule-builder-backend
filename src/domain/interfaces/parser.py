from abc import ABC, abstractmethod

from src.domain.dtos.booking import BookingWithTeacherAndGroup


class ICoursesParser(ABC):
    @abstractmethod
    def get_all_timeslots(
        self, spreadsheet_id: str
    ) -> list[BookingWithTeacherAndGroup]:
        pass
