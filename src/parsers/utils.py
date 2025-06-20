import datetime
import re
from pathlib import Path
# noinspection StandardLibraryXml
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openpyxl.utils import coordinate_to_tuple


TIMEZONE = "Europe/Moscow"


def nearest_weekday(date: datetime.date, day: int | str) -> datetime.date:
    """
    Returns the date of the next given weekday after
    the given date. For example, the date of next Monday.

    :param date: date to start from
    :type date: datetime.date
    :param day: weekday to find (0 is Monday, 6 is Sunday)
    :type day: int
    :return: date of the next given weekday
    :rtype: datetime.date
    """
    if isinstance(day, str):
        day = ["mo", "tu", "we", "th", "fr", "sa", "su"].index(day[:2].lower())

    days = (day - date.weekday() + 7) % 7
    return date + datetime.timedelta(days=days)


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent


def get_current_year() -> int:
    """Returns current year."""
    return datetime.datetime.now().year


def get_weekday_rrule(end_date: datetime.date) -> dict:
    """
    Get RRULE for recurrence with weekly interval and end date.

    :param end_date: end date
    :type end_date: datetime.date
    :return: RRULE dictionary with weekly interval and end date.
        See `here <https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html>`__
    :rtype: dict

    >>> get_weekday_rrule(datetime.date(2021, 1, 1))
    {'FREQ': 'WEEKLY', 'INTERVAL': 1, 'UNTIL': datetime.date(2021, 1, 1)}
    """
    return {
        "FREQ": "WEEKLY",
        "INTERVAL": 1,
        "UNTIL": end_date,
    }


# ----------------- Excel -----------------
def get_sheets(xlsx_zipfile: ZipFile) -> dict[str, str]:
    """
    Read xl/workbook.xml and return dict of sheet_id: sheet_name

    :param xlsx_zipfile: .xlsx file as ZipFile
    :return: dict of sheet_id: sheet_name
    """
    with xlsx_zipfile.open("xl/workbook.xml") as f:
        xml_struct = ET.parse(f)
    root = xml_struct.getroot()
    sheets = dict()
    for child in root:
        _, _, tag = child.tag.rpartition("}")
        if tag == "sheets":
            for sheet in child:
                sheet_id = sheet.attrib["sheetId"]
                sheet_name = sheet.attrib["name"]
                sheets[sheet_id] = sheet_name
            break
    return sheets


def get_sheet_by_id(xlsx_zipfile: ZipFile, sheet_id: str) -> ET.Element:
    """
    Read xl/worksheets/sheet{sheet_id}.xml and return root element

    :param xlsx_zipfile: .xlsx file as ZipFile
    :param sheet_id: id of sheet to read
    :return: root element of sheet
    """
    with xlsx_zipfile.open(f"xl/worksheets/sheet{str(sheet_id)}.xml") as f:
        xml_struct = ET.parse(f)
    root = xml_struct.getroot()
    return root


def get_namespace(element: ET.Element):
    """
    Get namespace from element tag

    :param element: element to get namespace from
    :return: namespace
    """
    m = re.match(r"{.*}", element.tag)
    return m.group(0) if m else ""


def get_merged_ranges(xlsx_sheet: ET.Element) -> list[str]:
    """
    Get list of merged ranges from sheet element

    :param xlsx_sheet: sheet element
    :return: list of merged ranges (e.g. ['A1:B2', 'C3:D4'])
    """
    namespace = get_namespace(xlsx_sheet)
    merged_cells = xlsx_sheet.find(f"{namespace}mergeCells")
    merged_ranges = []
    for merged_cell in merged_cells:
        merged_ranges.append(merged_cell.attrib["ref"])
    return merged_ranges


def split_range_to_xy(target_range: str):
    """
    Split range to x, y coordinates starting from 0

    :param target_range: range to split e.g. "A1:B2"
    :return: two points (x1, y1), (x2, y2)
    """
    start, end = target_range.split(":")
    start_row, start_col = coordinate_to_tuple(start)
    start_row, start_col = start_row - 1, start_col - 1
    end_row, end_col = coordinate_to_tuple(end)
    end_row, end_col = end_row - 1, end_col - 1
    return (start_row, start_col), (end_row, end_col)


def make_year_in_future(
    date: datetime.date, left_date: datetime.date
) -> datetime.date:
    """
    Set year from left date to date, returned date is always in the future
    """

    if date < left_date:
        date = date.replace(year=left_date.year + 1)
    else:
        date = date.replace(year=left_date.year)
    return date


def sluggify(s: str) -> str:
    """
    Sluggify string.

    :param s: string to sluggify
    :type s: str
    :return: sluggified string
    :rtype: str
    """
    s = s.lower()
    # also translates special symbols, brackets, commas, etc.
    s = re.sub(r"[^a-z0-9а-яА-ЯёЁ\s-]", " ", s)
    s = re.sub(r"\s+", "-", s)
    # remove multiple dashes
    s = re.sub(r"-{2,}", "-", s)
    return s
