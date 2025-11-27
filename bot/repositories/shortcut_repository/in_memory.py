from collections import defaultdict
from .base import ShortcutEntry, ShortcutRepository


class InMemoryShortcutRepository(ShortcutRepository):
    """Simple fallback repo when MySQL is not configured."""

    def __init__(self):
        self._data: defaultdict[int, list[ShortcutEntry]] = defaultdict(list)

    async def list(self, user_id: int):
        return list(self._data[user_id])

    async def add(self, user_id: int, command: str, city: str):
        shortcuts = self._data[user_id]

        for idx, (cmd, _) in enumerate(shortcuts):
            if cmd == command:
                shortcuts[idx] = (command, city)
                break
        else:
            shortcuts.append((command, city))

        return list(shortcuts)
