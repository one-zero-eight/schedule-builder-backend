from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.presentation.dependencies.parsers import CoursesParsersProvider
from src.presentation.dependencies.teacher import TeachersProvider
from src.presentation.dependencies.use_cases.collisions import (
    CollisionsCheckerProvider,
)


def create_async_container() -> AsyncContainer:
    container = make_async_container(
        FastapiProvider(),
        TeachersProvider(),
        CoursesParsersProvider(),
        CollisionsCheckerProvider(),
    )
    return container
