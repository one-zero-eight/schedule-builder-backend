from abc import ABC, abstractmethod

from src.domain.dtos.lesson import LessonWithDateDTO


class ICoursesParser(ABC):
    @abstractmethod
    async def get_all_timeslots(
        self, spreadsheet_id: str
    ) -> list[LessonWithDateDTO]:
        pass
