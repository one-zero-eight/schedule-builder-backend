from abc import ABC, abstractmethod

from src.domain.dtos.users import UserTokenDataDTO


class ITokenManager(ABC):
    @abstractmethod
    def verify_user_token(self, token: str) -> UserTokenDataDTO:
        pass
