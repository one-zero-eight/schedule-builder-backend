from dishka import Provider, Scope, provide

from src.domain.interfaces.parser import ICoursesParser
from src.parsers.core_courses.parser import CoreCoursesParser


class CoursesParsersProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_parser(self) -> ICoursesParser:
        return CoreCoursesParser()
