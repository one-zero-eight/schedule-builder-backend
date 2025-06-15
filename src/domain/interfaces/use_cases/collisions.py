from abc import ABC, abstractmethod


class ICollisionsChecker(ABC):
    @abstractmethod
    def get_collisions(self, google_sheet: str):
        pass
