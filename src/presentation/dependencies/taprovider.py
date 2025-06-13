from dishka import Provider, Scope, provide

from src.domain.interfaces.teacher_assistant_manager import (
    ITeacherAssistantManager,
)
from src.application.use_cases.teacher_assistant_manager import (
    TeacherAssistantManager,
)


class TeacherAssistantManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_manager(self) -> ITeacherAssistantManager:
        return TeacherAssistantManager()
