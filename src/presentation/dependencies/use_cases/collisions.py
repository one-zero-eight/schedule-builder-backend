from dishka import Provider, Scope, provide

from src.application.use_cases.collisions import CollisionsUseCase
from src.infrastructure.services.collisions_checker import CollisionsChecker
from src.parsers.core_courses.parser import CoreCoursesParser


class CollisionsUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_use_case(
        self,
        parser: CoreCoursesParser,
        collisions_checker: CollisionsChecker,
    ) -> CollisionsUseCase:
        return CollisionsUseCase(parser, collisions_checker)
