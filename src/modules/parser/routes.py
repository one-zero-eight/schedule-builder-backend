import json

import yaml
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, ValidationError

from src.api.dependencies import VerifyTokenDep
from src.core_courses.config import CoreCoursesConfig
from src.core_courses.location_parser import Item, parse_location_string
from src.electives.config import ElectivesParserConfig
from src.modules.collisions.core_courses_adapter import get_all_core_courses_lessons
from src.modules.collisions.electives_adapter import get_all_electives_lessons

router = APIRouter(prefix="/parser", tags=["Parser"])


class ParseLocationStringResponse(BaseModel):
    location_item: Item
    description: str


@router.post("/parse-location-string")
async def parse_location_string_route(
    _user_and_token: VerifyTokenDep, location_string: str
) -> ParseLocationStringResponse:
    location_item = parse_location_string(location_string)
    if location_item is None:
        raise HTTPException(status_code=400, detail="Invalid location string")
    return ParseLocationStringResponse(
        location_item=location_item,
        description=location_item.describe_calendar_behavior(),
    )


@router.post("/parse-core-courses")
async def parse_core_courses_route(
    _user_and_token: VerifyTokenDep, input: str = Body(media_type="text/yaml")
) -> Response:
    try:
        payload = yaml.safe_load(input) or {}
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail="Invalid request body format") from e

    try:
        parser_config = CoreCoursesConfig.model_validate(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e

    lessons = await get_all_core_courses_lessons(parser_config)
    as_json = [lesson.model_dump(mode="json") for lesson in lessons]
    targets = {t.sheet_name: t for t in parser_config.targets}
    for lesson in as_json:
        target = targets[lesson["google_sheet_name"]]
        lesson["start_date"] = target.start_date.isoformat()
        lesson["end_date"] = target.end_date.isoformat()

    content = json.dumps(as_json, indent=2, ensure_ascii=False)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="core-courses-lessons.json"'},
    )


@router.post("/parse-electives")
async def parse_electives_route(_user_and_token: VerifyTokenDep, input: str = Body(media_type="text/yaml")) -> Response:
    try:
        payload = yaml.safe_load(input) or {}
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail="Invalid request body format") from e

    try:
        parser_config = ElectivesParserConfig.model_validate(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e

    lessons = await get_all_electives_lessons(parser_config)
    as_json = [lesson.model_dump(mode="json") for lesson in lessons]

    content = json.dumps(as_json, indent=2, ensure_ascii=False)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="electives-lessons.json"'},
    )
