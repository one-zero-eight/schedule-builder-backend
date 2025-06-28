from dishka import Provider, Scope, provide

from src.application.use_cases.collisions import CollisionsUseCase
from src.domain.interfaces.services.collisions_checker import (
    ICollisionsChecker,
)
from src.domain.interfaces.services.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsUseCase


class CollisionsUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_use_case(
        self,
        parser: ICoursesParser,
        collisions_checker: ICollisionsChecker,
    ) -> ICollisionsUseCase:
        return CollisionsUseCase(parser, collisions_checker)
