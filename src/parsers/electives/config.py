import json
from pathlib import Path

from pydantic import BaseModel, field_validator, parse_obj_as

from src.parsers.electives.models import Elective


CONFIG_PATH = Path(__file__).parent / "config.json"
"""Path to config.json file"""


class ElectivesParserConfig(BaseModel):
    """
    Config for electives parser from Google Sheets
    """

    class Target(BaseModel):
        """
        Target model for electives (sheet in Google Sheets)
        """

        sheet_name: str
        range: str

    TARGETS: list[Target]

    class Tag(BaseModel):
        alias: str
        type: str
        name: str

    SEMESTER_TAG: Tag

    SPREADSHEET_ID: str
    DISTRIBUTION_SPREADSHEET_ID: str | None = None

    ELECTIVES: list["Elective"]


with open(CONFIG_PATH) as f:
    elective_config_dict = json.load(f)

electives_config: ElectivesParserConfig = parse_obj_as(
    ElectivesParserConfig, elective_config_dict
)
