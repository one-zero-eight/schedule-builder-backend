from dishka import Provider, Scope, provide
from yaml import safe_load

from src.domain.dtos.teacher import TeacherDTO


class TeachersProvider(Provider):
    scope = Scope.APP

    @provide
    def get_teachers(self) -> list[TeacherDTO]:
        teachers = list()
        with open("teachers.yaml", "r", encoding="utf-8") as file:
            data = safe_load(file)
            for teacher in data["teachers"]:
                teachers.append(
                    TeacherDTO(
                        name=teacher["name"],
                        group=teacher["study_group"],
                        email=teacher["email"],
                    )
                )
        return teachers
