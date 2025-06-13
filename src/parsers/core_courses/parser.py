import io
from datetime import datetime
from hashlib import sha1
from itertools import chain, pairwise
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests
from openpyxl.utils import column_index_from_string

from src.domain.interfaces.parser import ICoursesParser
from src.domain.dtos.booking import BookingWithTeacherAndGroup
from src.parsers.core_courses.config import core_courses_config as config
from src.parsers.processors.regex import prettify_string
from src.parsers.utils import (
    get_merged_ranges,
    get_sheet_by_id,
    get_sheets,
    split_range_to_xy,
)


# noinspection InsecureHash
def hashsum_dfs(dfs: dict[str, pd.DataFrame]) -> str:
    to_hash = (
        sha1(
            pd.util.hash_pandas_object(dfs[target.sheet_name]).values
        ).hexdigest()
        for target in config.TARGETS
    )
    hashsum = sha1("\n".join(to_hash).encode("utf-8")).hexdigest()
    return hashsum


def get_dataframes_pipeline(parser, xlsx) -> dict[str, pd.DataFrame]:
    dfs = parser.get_clear_dataframes_from_xlsx(
        xlsx_file=xlsx, targets=config.TARGETS
    )
    hashsum = hashsum_dfs(dfs)

    xlsx_path = config.TEMP_DIR / f"{hashsum}.xlsx"
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    with open(xlsx_path, "wb") as f:
        xlsx.seek(0)
        content = xlsx.read()
        f.write(content)

    return dfs


class CoreCoursesParser(ICoursesParser):
    """
    Elective parser class
    """

    #
    # credentials: Credentials
    # """ Google API credentials object """

    def __init__(self):
        self.session = requests.Session()

    def get_clear_dataframes_from_xlsx(
        self, xlsx_file: io.BytesIO, targets: list[config.Target]
    ) -> dict[str, pd.DataFrame]:
        """
        Get data from xlsx file and return it as a DataFrame with merged
        cells and empty cells in the course row filled by left value.

        :param xlsx_file: xlsx file with data
        :type xlsx_file: io.BytesIO
        :param targets: list of targets to get data from (sheets and ranges)
        :type targets: list[config.Target]

        :return: dataframes with merged cells and empty cells filled
        :rtype: dict[str, pd.DataFrame]
        """
        # ------- Read xlsx file into dataframes -------
        dfs = pd.read_excel(
            xlsx_file, engine="openpyxl", sheet_name=None, header=None
        )
        # ------- Clean up dataframes -------
        dfs = {key.strip(): value for key, value in dfs.items()}

        for target in targets:
            df = None
            for key, value in dfs.items():
                if key.startswith(target.sheet_name):
                    df = value
                    break
            # -------- Fill merged cells with values --------
            self.merge_cells(df, xlsx_file, target.sheet_name)
            # -------- Select range --------
            df = self.select_range(df, target.range)
            # -------- Fill empty cells --------
            df = df.replace(r"^\s*$", np.nan, regex=True)
            # -------- Strip, translate and remove trailing spaces --------
            df = df.map(prettify_string)
            # -------- Update dataframe --------
            dfs[target.sheet_name] = df

        return dfs

    def get_xlsx_file(self, spreadsheet_id: str) -> io.BytesIO:
        """
        Export xlsx file from Google Sheets and return it as BytesIO object.

        :param spreadsheet_id: id of Google Sheets spreadsheet
        :return: xlsx file as BytesIO object
        """
        # ------- Get data from Google Sheets -------
        # ------- Create url for export -------
        spreadsheet_url = (
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        )
        export_url = spreadsheet_url + "/export?format=xlsx"
        # ------- Export xlsx file -------
        response = self.session.get(export_url)
        response.raise_for_status()
        # ------- Return xlsx file as BytesIO object -------
        return io.BytesIO(response.content)

    def merge_cells(
        self, df: pd.DataFrame, xlsx: io.BytesIO, target_sheet_name: str
    ):
        """
        Merge cells in dataframe

        :param df: Dataframe to process
        :param xlsx: xlsx file with data
        :param target_sheet_name: sheet to process
        """
        xlsx.seek(0)
        xlsx_zipfile = ZipFile(xlsx)
        sheets = get_sheets(xlsx_zipfile)
        target_sheet_id = None
        for sheet_id, sheet_name in sheets.items():
            if target_sheet_name in sheet_name:
                target_sheet_id = sheet_id
                break
        sheet = get_sheet_by_id(xlsx_zipfile, target_sheet_id)
        merged_ranges = get_merged_ranges(sheet)

        # ------- Merge cells -------
        for merged_range in merged_ranges:
            (start_row, start_col), (end_row, end_col) = split_range_to_xy(
                merged_range
            )
            # get value from top left cell
            value = df.iloc[start_row, start_col]
            # fill merged cells with value
            df.iloc[start_row : end_row + 1, start_col : end_col + 1] = value

    def select_range(
        self, df: pd.DataFrame, target_range: str
    ) -> pd.DataFrame:
        """
        Select range from dataframe

        :param df: dataframe to process
        :type df: pd.DataFrame
        :param target_range: range to select
        :type target_range: str
        :return: selected range
        :rtype: pd.DataFrame
        """
        (start_row, start_col), (end_row, end_col) = split_range_to_xy(
            target_range
        )
        return df.iloc[
            start_row : end_row + 1,
            start_col : end_col + 1,
        ]

    def set_weekday_and_time_as_index(
        self, df: pd.DataFrame, column: int = 0
    ) -> pd.DataFrame:
        """
        Set time column as index and process it to datetime format

        :param df: dataframe to process
        :type df: pd.DataFrame
        :param column: column to set as index, defaults to 0
        :type column: int, optional
        """

        # get column view and iterate over it
        df_column = df.iloc[:, column]
        df_column: pd.Series
        # drop column
        df.drop(df.columns[column], axis=1, inplace=True)
        # fill nan values with previous value
        df_column.ffill(inplace=True)

        # ----- Process weekday ------ #
        # get indexes of weekdays
        weekdays_indexes = [
            i
            for i, cell in enumerate(df_column.values)
            if cell in config.WEEKDAYS
        ]

        # create index mapping for weekdays [None, None, "MONDAY", "MONDAY", ...]
        index_mapping = pd.Series(index=df_column.index, dtype=object)
        last_index = len(df_column)
        for start, end in pairwise(weekdays_indexes + [last_index]):
            index_mapping.iloc[start] = "delete"
            index_mapping.iloc[start + 1 : end] = df_column[start]

        # ----- Process time ------ #
        # matched r"\d{1,2}:\d{2}-\d{1,2}:\d{2}" regex

        matched = df_column[
            df_column.str.match(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}")
        ]

        for i, cell in matched.items():
            # "9:00-10:30" -> datetime.time(9, 0), datetime.time(10, 30)
            start, end = cell.split("-")
            df_column.loc[i] = (
                datetime.strptime(start, "%H:%M").time(),
                datetime.strptime(end, "%H:%M").time(),
            )

        # create multiindex from index mapping and time column
        multiindex = pd.MultiIndex.from_arrays(
            [index_mapping, df_column], names=["weekday", "time"]
        )
        # set multiindex as index
        df.set_index(multiindex, inplace=True)
        # drop rows with weekday
        df.drop("delete", inplace=True, level=0)
        return df

    def set_course_and_group_as_header(
        self, df: pd.DataFrame, rows: tuple = (0, 1)
    ) -> pd.DataFrame:
        """
        Set course and group as header

        :param df: dataframe to process
        :type df: pd.DataFrame
        :param rows: row to set as columns, defaults to (0, 1)
        :type rows: tuple, optional
        """
        # ------- Set course and group as header -------
        # get rows with course and group
        df_header = df.iloc[rows[0] : rows[1] + 1]
        # drop rows with course and group
        df.drop(list(rows), inplace=True)
        df.reset_index(drop=True, inplace=True)
        # fill nan values with previous value
        with pd.option_context("future.no_silent_downcasting", True):
            df_header = df_header.ffill(axis=1)
        multiindex = pd.MultiIndex.from_arrays(
            df_header.values, names=["course", "group"]
        )
        df.columns = multiindex
        return df

    def split_df_by_courses(
        self, df: pd.DataFrame, time_columns: list[int]
    ) -> list[pd.DataFrame]:
        """
        Split dataframe by "Week *" rows

        :param time_columns: list of columns(pd) with time and weekday
        :param df: dataframe to split
        :type df: pd.DataFrame
        :return: list of dataframes with locators
        :rtype: list[pd.DataFrame, ExcelToPandasLocator]
        """

        time_columns_indexes = time_columns

        # split dataframe by found columns
        _, max_y = df.shape
        split_indexes = time_columns_indexes + [max_y]

        split_dfs = []

        for _, (start, end) in enumerate(pairwise(split_indexes)):
            split_df = df.iloc[:, start:end].copy()
            split_dfs.append(split_df)
        return split_dfs

    def get_all_timeslots(
        self, spreadsheet_id: str
    ) -> list[BookingWithTeacherAndGroup]:
        xlsx = self.get_xlsx_file(spreadsheet_id=spreadsheet_id)
        dfs = get_dataframes_pipeline(self, xlsx)

        events = []

        for target in config.TARGETS:
            # find dataframe from dfs
            sheet_df = dfs[target.sheet_name]

            time_columns_index = [
                column_index_from_string(col) - 1
                for col in target.time_columns
            ]
            by_courses = self.split_df_by_courses(sheet_df, time_columns_index)
            for course_df in by_courses:
                # -------- Set course and group as header; weekday and timeslot as index --------
                self.set_course_and_group_as_header(course_df)
                self.set_weekday_and_time_as_index(course_df)
                event_generators = course_df.groupby(level=[0, 1], sort=False)
                events.extend(event_generators)

        timeslots_objects = []
        for timeslot, timeslot_df in events:
            weekday, (start_time, end_time) = timeslot
            for column, cell_values_series in timeslot_df.items():
                cell_values_series: pd.Series
                year, group = column
                if pd.isna(cell_values_series).all():
                    continue
                else:
                    subject, teacher, location = cell_values_series.values
                timeslots_objects.append(
                    BookingWithTeacherAndGroup(
                        weekday=weekday,
                        start=start_time,
                        end=end_time,
                        group=group,
                        teacher=teacher,
                        room=location,
                    )
                )

        return timeslots_objects
