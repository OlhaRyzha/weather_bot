from abc import ABC, abstractmethod
from typing import Tuple

ShortcutEntry = Tuple[str, str]


class ShortcutRepository(ABC):
    @abstractmethod
    async def list(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def add(self, user_id: int, command: str, city: str):
        raise NotImplementedError
