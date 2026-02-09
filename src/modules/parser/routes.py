from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.dependencies import VerifyTokenDep
from src.core_courses.location_parser import Item, parse_location_string

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
