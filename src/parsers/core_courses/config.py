import datetime
import json
from pathlib import Path

from pydantic import BaseModel, parse_obj_as


CONFIG_PATH = Path(__file__).parent / "config.json"


class CoreCoursesConfig(BaseModel):
    """
    Config for electives parser from Google Sheets
    """

    class Target(BaseModel):
        """
        Target model
        """

        sheet_name: str
        """Sheet name"""
        range: str
        """Range"""
        time_columns: list[str]
        """Time columns"""
        start_date: datetime.date
        """Datetime start"""
        end_date: datetime.date
        """Datetime end"""

    TARGETS: list[Target]
    """List of targets"""
    SPREADSHEET_ID: str
    WEEKDAYS: list[str] = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]


with open(CONFIG_PATH, "r") as f:
    elective_config_dict = json.load(f)

core_courses_config: CoreCoursesConfig = parse_obj_as(
    CoreCoursesConfig, elective_config_dict
)
