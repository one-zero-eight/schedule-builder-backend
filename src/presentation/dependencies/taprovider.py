from dishka import Provider, Scope, provide
from yaml import safe_load

from src.domain.dtos.teacher import TeacherDTO


class TeacherAssistantManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_teachers(self, file_path: str) -> list[TeacherDTO]:
        assistants = list()
        with open(file_path, "r", encoding="utf-8") as file:
            data = safe_load(file)
            for teacher in data["staff"]:
                assistant = TeacherDTO(
                    name=teacher["name"], group=teacher["group"]
                )
                assistants.append(assistant)
        return assistants
