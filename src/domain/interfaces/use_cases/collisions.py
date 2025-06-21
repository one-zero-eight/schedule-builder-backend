from abc import ABC, abstractmethod


class ICollisionsChecker(ABC):
    @abstractmethod
    def get_collisions(
        self,
        google_sheet: str,
        check_room_collisions: bool = True,
        check_teacher_collisions: bool = True,
        check_space_collisions: bool = True,
        check_outlook_collisions: bool = True,
    ):
        pass


class IOutlookCollisionsChecker(ABC):
    @abstractmethod
    def get_outlook_collisions(self):
        pass
