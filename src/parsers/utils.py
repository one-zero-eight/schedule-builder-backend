import datetime
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openpyxl.utils import coordinate_to_tuple


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


def split_range_to_xy(
    target_range: str,
) -> tuple[tuple[int, int], tuple[int, int]]:
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


def get_current_year() -> int:
    """Returns current year."""
    return datetime.datetime.now().year
