from abc import abstractmethod, ABC
from src.domain.dtos.teachers import TeacherAssistant


class ITeacherAssistantManager(ABC):
    @abstractmethod
    def load_teacher_assistants(
        self, file_path: str
    ) -> list[TeacherAssistant]:
        pass
