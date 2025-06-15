from abc import ABC, abstractmethod

from authlib.jose import JsonWebKey

from src.domain.dtos.users import UserDTO


class IInNoHassleAccounts(ABC):
    @abstractmethod
    def get_public_key(self) -> JsonWebKey:
        pass
