from dishka import Provider, Scope, provide

from src.application.use_cases.collisions import CollisionsChecker
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


class CollisionsCheckerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_collisions_checker(
        self, parser: ICoursesParser
    ) -> ICollisionsChecker:
        return CollisionsChecker(parser)
