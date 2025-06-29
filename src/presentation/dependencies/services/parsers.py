from dishka import Provider, Scope, provide

from src.domain.interfaces.services.parser import ICoursesParser
from src.parsers.core_courses.parser import CoreCoursesParser


class CoursesParserProvider(Provider):
    scope = Scope.APP

    @provide
    def get_parser(self) -> ICoursesParser:
        return CoreCoursesParser()
