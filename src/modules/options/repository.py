import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.core_courses.config import Target
from src.custom_pydantic import CustomModel
from src.logging_ import logger


class SemesterOptions(CustomModel):
    name: str
    core_courses_spreadsheet_id: str | None = None
    core_courses_targets: list[Target] = []

    electives_spreadsheet_id: str | None = None


class Teacher(CustomModel):
    name: str
    email: str | None = None
    alias: str | None = None
    student_group: str | None = None  # e.g. "B4-CSE-05"


class TeachersData(CustomModel):
    data: list[Teacher] = []


class OptionsData(CustomModel):
    semester: SemesterOptions | None = None
    teachers: TeachersData | None = None


class OptionsRepository:
    def __init__(self, file_path: str = "data/options.json"):
        self.file_path = Path(file_path)

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self._save_data(OptionsData())

    def _load_data(self) -> OptionsData:
        self._ensure_file_exists()
        with open(self.file_path) as f:
            data = json.load(f)
        return OptionsData.model_validate(data)

    def _save_data(self, data: OptionsData) -> None:
        with open(
            self.file_path,
            "w",
        ) as f:
            json.dump(data.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    def get_semester(self) -> SemesterOptions | None:
        data = self._load_data()
        return data.semester

    def set_semester(self, semester: SemesterOptions) -> None:
        data = self._load_data()
        data.semester = semester
        self._save_data(data)

    def get_all_options(self) -> OptionsData:
        return self._load_data()

    def set_teachers_from_csv_text(self, csv_text: str) -> TeachersData:
        from io import StringIO

        # remove all empty rows
        csv_text = "\n".join([line for line in csv_text.splitlines() if line.strip()])

        df: pd.DataFrame = pd.read_csv(StringIO(csv_text), sep="\t")  # pyright: ignore[reportCallIssue]

        # Normalize column names to lowercase
        df.columns = df.columns.str.lower()
        # Detect name column: "name" or "unnamed: 0"
        name_col = "name" if "name" in df.columns else "unnamed: 0"
        df.rename(
            columns={name_col: "name", "email": "email", "alias": "alias", "student group": "student_group"},
            inplace=True,
        )
        df = df[["name", "alias", "email", "student_group"]]  # pyright: ignore[reportAssignmentType]
        df.replace(to_replace=np.nan, value=None, inplace=True)
        df.replace(to_replace="-", value=None, inplace=True)
        df.loc[df["alias"] == "?", "alias"] = None
        # strip all strings
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        # remove nan values in name column
        logger.info(f"Loaded teachers from CSV:\n{df.head(5)}")
        records = df.to_dict(orient="records")
        teachers_data = []
        for row in records:
            if row["name"] is None or pd.isna(row["name"]):
                continue

            if not pd.isna(row["student_group"]) or not pd.isna(row["alias"]) or not pd.isna(row["email"]):
                teachers_data.append(Teacher.model_validate(row))

        teachers_data = TeachersData(data=teachers_data)

        data = self._load_data()
        data.teachers = teachers_data
        self._save_data(data)

        return teachers_data

    def get_teachers(self) -> TeachersData | None:
        data = self._load_data()
        return data.teachers


options_repository: OptionsRepository = OptionsRepository()
