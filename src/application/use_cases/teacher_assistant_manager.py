from yaml import safe_load

from src.domain.dtos.teacher import TeacherDTO
from src.domain.interfaces.teacher_assistant_manager import (
    ITeacherAssistantManager,
)


class TeacherAssistantManager(ITeacherAssistantManager):

    @classmethod
    def load_teacher_assistants(self, file_path: str) -> list[TeacherDTO]:
        teacher_assistants = list()
        with open(file_path, "r", encoding="UTF-8") as file:
            data = safe_load(file)
            for teacher in data["staff"]:
                assistant = TeacherDTO(
                    name=teacher["name"], group=teacher["group"]
                )
                teacher_assistants.append(assistant)
        return teacher_assistants
