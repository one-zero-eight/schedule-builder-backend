from collections import defaultdict

from src.domain.dtos.booking import BookingWithTeacherAndGroup
from src.domain.interfaces.parser import ICoursesParser
from src.domain.interfaces.use_cases.collisions import ICollisionsChecker


class CollisionsChecker(ICollisionsChecker):
    def __init__(self, parser: ICoursesParser) -> None:
        self.parser = parser

    def check_two_timeslots_collisions_by_time(
        self,
        slot1: BookingWithTeacherAndGroup,
        slot2: BookingWithTeacherAndGroup,
    ) -> bool:
        if (
            slot2.start < slot1.start < slot2.end
            or slot2.start < slot1.end < slot2.end
        ):
            return True
        if (
            slot1.start < slot2.start < slot1.end
            or slot1.start < slot2.end < slot1.end
        ):
            return True
        return False

    def is_online_slot(slot: BookingWithTeacherAndGroup) -> bool:
        return "ONLINE" == slot.location

    def get_collsisions_by_room(
        self, timeslots: list[BookingWithTeacherAndGroup]
    ) -> list[tuple[BookingWithTeacherAndGroup, BookingWithTeacherAndGroup]]:
        weekday_to_room_to_slots = defaultdict(lambda: defaultdict(list))
        for slot in timeslots:
            weekday_to_room_to_slots[slot.weekday][slot.room].append(slot)
        collisions = []
        for weekday in weekday_to_room_to_slots:
            for room in weekday_to_room_to_slots[weekday]:
                n = len(weekday_to_room_to_slots[weekday][room])
                for i in range(n):
                    slot1 = weekday_to_room_to_slots[weekday][room][i]
                    if self.is_online_slot(slot1):
                        continue
                    for j in range(i + 1, n):
                        slot2 = weekday_to_room_to_slots[weekday][room][j]
                        if self.is_online_slot(slot2):
                            continue
                        if self.check_two_timeslots_collisions_by_time(
                            slot1, slot2
                        ):
                            collisions.append((slot1, slot2))
                            break
        return collisions

    def check_collisions(self, spreadsheet_id: str) -> dict[
        str,
        list[tuple[BookingWithTeacherAndGroup, BookingWithTeacherAndGroup]],
    ]:
        timeslots: list[BookingWithTeacherAndGroup] = (
            self.parser.get_all_timeslots(spreadsheet_id)
        )
        collisions = dict()
        collisions["room"] = self.get_collsisions_by_room(timeslots)
        return collisions
