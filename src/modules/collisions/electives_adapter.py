from src.electives.cell_to_event import ElectiveEvent
from src.electives.config import ElectivesParserConfig
from src.electives.parser import ElectiveParser
from src.logging_ import logger
from src.utils import WEEKDAYS, fetch_xlsx_spreadsheet, get_sheet_gids

from .schemas import Lesson


async def get_all_electives_lessons(parser_config: ElectivesParserConfig) -> list[Lesson]:
    parser = ElectiveParser()
    xlsx_file = await fetch_xlsx_spreadsheet(spreadsheet_id=parser_config.spreadsheet_id)
    original_target_sheet_names = [target.sheet_name for target in parser_config.targets]
    sheet_gids = await get_sheet_gids(parser_config.spreadsheet_id)
    pipeline_result = list(
        parser.pipeline(
            xlsx_file, original_target_sheet_names, parser_config.electives, sheet_gids, parser_config.spreadsheet_id
        )
    )

    all_lessons: list[Lesson] = []
    for target, separations_list in zip(parser_config.targets, pipeline_result):
        for separation in separations_list:
            for event in separation.events:
                lesson = _event_to_lesson(event)
                if lesson:
                    all_lessons.append(lesson)

        logger.info(
            f"For {target.sheet_name} found {len([s for s in separations_list for _ in s.events])} elective events"
        )

    def _sort_key(x: Lesson):
        group = x.group_name
        if group is None:
            group = ()
        elif isinstance(group, str):
            group = (group,)
        return (x.course_name or "", group, x.weekday or "", x.start_time)

    all_lessons.sort(key=_sort_key)
    return all_lessons


def _event_to_lesson(event: ElectiveEvent) -> Lesson | None:
    """
    Convert ElectiveEvent to Lesson
    """
    weekday_name = WEEKDAYS[event.start.weekday()]
    start_time = event.start.time()
    end_time = event.end.time()

    lesson_name = event.elective.name or event.elective.alias
    course_name = event.elective.alias
    teacher = event.elective.instructor

    return Lesson(
        lesson_name=lesson_name,
        weekday=weekday_name,
        start_time=start_time,
        end_time=end_time,
        course_name=course_name,
        group_name=event.group,
        teacher=teacher,
        room=event.location,
        date_on=[event.start.date()] if event.start else None,
        date_except=None,
        students_number=None,
        spreadsheet_id=event.spreadsheet_id,
        google_sheet_gid=event.google_sheet_gid,
        google_sheet_name=event.google_sheet_name,
        a1_range=event.a1,
    )
