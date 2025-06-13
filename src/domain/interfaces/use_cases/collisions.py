from abc import ABC, abstractmethod


class ICollisionsChecker(ABC):
    @abstractmethod
    def check_collisions(self, google_sheet: str):
        pass
