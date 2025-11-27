from typing import Optional
from .base import ShortcutRepository
from .in_memory import InMemoryShortcutRepository


class ShortcutStorageProxy(ShortcutRepository):
    """Proxy that lets us switch storage backend at runtime."""

    def __init__(self, backend: Optional[ShortcutRepository] = None):
        self._backend: ShortcutRepository = backend or InMemoryShortcutRepository()

    def set_backend(self, backend: ShortcutRepository):
        self._backend = backend

    async def list(self, user_id: int):
        return await self._backend.list(user_id)

    async def add(self, user_id: int, command: str, city: str):
        return await self._backend.add(user_id, command, city)


shortcuts_storage = ShortcutStorageProxy()
