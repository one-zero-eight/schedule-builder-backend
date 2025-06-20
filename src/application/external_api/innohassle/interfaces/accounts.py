from abc import ABC, abstractmethod

from authlib.jose import JsonWebKey



class IInNoHassleAccounts(ABC):
    @abstractmethod
    def get_public_key(self) -> JsonWebKey:
        pass
