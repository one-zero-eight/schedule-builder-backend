import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class SettingBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class Accounts(SettingBaseModel):
    """InNoHassle Accounts integration settings"""

    api_url: str = "https://api.innohassle.ru/accounts/v0/"
    "URL of the Accounts API"
    api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"


class Booking(SettingBaseModel):
    """Booking API integration settings"""

    api_url: str = "https://api.innohassle.ru/room-booking/staging-v0/"
    "URL of the Booking API"


class TeacherDTO(SettingBaseModel):
    name: str
    "First and second name of teacher"
    group: str
    "Group of a teacher"
    email: str
    "Email of teacher"


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
        start_date: datetime.date
        """Datetime start"""
        end_date: datetime.date
        """Datetime end"""

    targets: list[Target]
    """List of targets"""


class Settings(SettingBaseModel):
    """Settings for the application."""

    schema_: str = Field(None, alias="$schema")  # type: ignore
    app_root_path: str = ""
    'Prefix for the API path (e.g. "/api/v0")'
    cors_allow_origin_regex: str = ".*"
    "Allowed origins for CORS: from which domains requests to the API are allowed. Specify as a regex: `https://.*.innohassle.ru`"
    accounts: Accounts
    "InNoHassle Accounts integration settings"
    booking: Booking = Booking()
    "Booking API integration settings"
    teachers: list[TeacherDTO]
    "List of teachers"
    core_courses_config: CoreCoursesConfig
    "Config for core courses parser from Google Sheets"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {
                "$schema": "https://json-schema.org/draft-07/schema",
                **cls.model_json_schema(),
            }
            yaml.dump(schema, f, sort_keys=False)
