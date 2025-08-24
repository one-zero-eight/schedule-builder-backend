import re

from openpyxl.utils import coordinate_to_tuple


def sanitize_sheet_name(name: str) -> str:
    r"""Convert any string to a valid Excel sheet name following Google Sheets export behavior.

    Excel sheet name restrictions:
    - Max 31 characters
    - Cannot contain: / \ ? * [ ] :
    - Cannot start/end with single quotes
    """
    if not name or not name.strip():
        return "Sheet1"

    name = name.strip()
    name = re.sub(r"[/\\?*\[\]:]", "", name)
    name = name.strip("'")

    if len(name) > 31:
        name = name[:31].rstrip()

    if not name or name.isspace():
        return "Sheet1"

    return name


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
