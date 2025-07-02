import datetime
import re
from typing import Optional, Any

from pydantic import BaseModel, field_validator, Field

from src.parsers.processors.regex import process_spaces


class Elective(BaseModel):
    """
    Elective model for ElectivesParserConfig
    """

    alias: str
    """Alias for elective"""
    name: Optional[str]
    """Name of elective"""
    instructor: Optional[str]
    """Instructor of elective"""
    elective_type: Optional[str]
    """Type of elective"""

    @field_validator("name", "instructor", "elective_type", pre=True)
    def beatify_string(cls: type["Elective"], string: str) -> str:
        """Beatify string

        :param string: string to beatify
        :type string: str
        :return: beatified string
        :rtype: str
        """
        if string:
            string = process_spaces(string)
        return string


class ElectiveCell(BaseModel):
    original: list[str]
    """ Original cell value """

    class Occurrence(BaseModel):
        """Occurrence of the elective"""

        original: str
        """ Original occurrence value """
        elective: Optional[Elective]
        """ Elective object """
        location: Optional[str]
        """ Location of the elective """
        group: Optional[str]
        """ Group to which the elective belongs """
        class_type: Optional[str]
        """ Type of the class(leture, seminar, etc.) """
        starts_at: Optional[datetime.time]
        """ Time when the elective starts (modificator) """
        ends_at: Optional[datetime.time]
        """ Time when the elective ends (modificator) """

        def __init__(self, **data: Any):
            """
            Process cell value

            - GAI (lec) online
            - PHL 101
            - PMBA (lab) (Group 1) 313
            - GDU 18:00-19:30 (lab) 101
            - OMML (18:10-19:50) 312
            - PGA 300
            - IQC (17:05-18:35) online
            - SMP online
            - ASEM (starts at 18:05) 101
            """

            from src.parsers.electives.config import electives_config as config

            super().__init__(**data)

            string = self.original.strip()
            # just first word as elective
            splitter = string.split(" ")
            elective_alias = splitter[0]
            self.elective = next(elective for elective in config.ELECTIVES if elective.alias == elective_alias)
            string = " ".join(splitter[1:])
            # find time xx:xx-xx:xx

            if timeslot_m := re.search(r"\(?(\d{2}:\d{2})-(\d{2}:\d{2})\)?", string):
                self.starts_at = datetime.datetime.strptime(timeslot_m.group(1), "%H:%M").time()
                self.ends_at = datetime.datetime.strptime(timeslot_m.group(2), "%H:%M").time()
                string = string.replace(timeslot_m.group(0), "")

            # find starts at xx:xx
            if timeslot_m := re.search(r"\(?starts at (\d{2}:\d{2})\)?", string):
                self.starts_at = datetime.datetime.strptime(timeslot_m.group(1), "%H:%M").time()
                string = string.replace(timeslot_m.group(0), "")

            # find (lab), (lec)
            if class_type_m := re.search(r"\(?(lab|lec)\)?", string, flags=re.IGNORECASE):
                self.class_type = class_type_m.group(1).lower()
                string = string.replace(class_type_m.group(0), "")

            # find (G1)
            if group_m := re.search(r"\(?(G\d+)\)?", string):
                self.group = group_m.group(1)
                string = string.replace(group_m.group(0), "")

            # find location (what is left)
            string = string.strip()
            if string:
                self.location = string

    occurrences: list[Occurrence] = Field(default_factory=list)
    """ List of occurrences of the electives """

    def __init__(self, **data: Any):
        super().__init__(**data)
        for line in self.original:
            self.occurrences.append(self.Occurrence(original=line))
