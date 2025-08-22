from dishka import Provider, Scope, provide

from src.parsers.core_courses.parser import CoreCoursesParser


class CoursesParserProvider(Provider):
    scope = Scope.APP

    @provide
    def get_parser(self) -> CoreCoursesParser:
        return CoreCoursesParser()
