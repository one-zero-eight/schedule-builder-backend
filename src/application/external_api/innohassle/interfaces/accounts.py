from abc import ABC, abstractmethod

from authlib.jose import JsonWebKey

from src.domain.dtos.users import UserDTO


class IInNoHassleAccounts(ABC):
    @abstractmethod
    def get_public_key(self) -> JsonWebKey:
        pass

    @abstractmethod
    def get_user_by_id(self, innohassle_id: str) -> UserDTO | None:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserDTO | None:
        pass
