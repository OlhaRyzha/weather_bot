from .base import ShortcutEntry, ShortcutRepository
from .in_memory import InMemoryShortcutRepository
from .mysql import MySQLShortcutRepository
from .storage import ShortcutStorageProxy, shortcuts_storage

__all__ = [
    "ShortcutEntry",
    "ShortcutRepository",
    "InMemoryShortcutRepository",
    "MySQLShortcutRepository",
    "ShortcutStorageProxy",
    "shortcuts_storage",
]
