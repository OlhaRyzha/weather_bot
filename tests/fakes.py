from dataclasses import dataclass, field
from typing import TypeAlias, TypedDict


@dataclass
class FakeUser:
    """Lightweight stand-in for aiogram.types.User."""

    id: int = 1
    first_name: str = "Test"
    last_name: str = "User"

    @property
    def full_name(self) -> str:
        return " ".join(
            part for part in (self.first_name, self.last_name) if part
        ).strip()


@dataclass
class FakeLocation:
    """Simple location holder that mimics aiogram Location."""

    latitude: float
    longitude: float


class MessageUpdate(TypedDict, total=False):
    text: str | None
    user: FakeUser | None
    location: FakeLocation | None


AnswerRecord: TypeAlias = dict[str, object]
PhotoRecord: TypeAlias = dict[str, object]


@dataclass
class FakeMessageLog:
    answers: list[AnswerRecord]
    photos: list[PhotoRecord]


class FakeMessage:
    """Async-friendly test double for aiogram Message."""

    def __init__(
        self,
        *,
        text: str | None = "",
        user: FakeUser | None = None,
        location: FakeLocation | None = None,
        log: FakeMessageLog | None = None,
    ):
        self.text = text
        self.from_user = user or FakeUser()
        self.location = location
        self._log = log or FakeMessageLog(answers=[], photos=[])

    @property
    def answers(self) -> list[AnswerRecord]:
        return self._log.answers

    @property
    def photo_answers(self) -> list[PhotoRecord]:
        return self._log.photos

    async def answer(self, text: str, **kwargs: object) -> None:
        self._log.answers.append({"text": text, **kwargs})

    async def answer_photo(
        self,
        *,
        photo: object,
        caption: str,
        **kwargs: object,
    ) -> None:
        self._log.photos.append({"photo": photo, "caption": caption, **kwargs})

    def model_copy(self, update: MessageUpdate | None = None) -> "FakeMessage":
        text = self.text
        user = self.from_user
        location = self.location

        if update:
            if "text" in update:
                text = update["text"]
            if "user" in update:
                user = update["user"]
            if "location" in update:
                location = update["location"]

        return FakeMessage(
            text=text,
            user=user,
            location=location,
            log=self._log,
        )


@dataclass
class FakeFSMContext:
    """Minimal async FSMContext replacement for router tests."""

    state: object | None = None
    data: dict[str, object] = field(default_factory=dict)
    log: list[tuple[str, object | None]] = field(default_factory=list)

    async def set_state(self, state):
        self.state = state
        self.log.append(("set_state", state))

    async def clear(self):
        self.state = None
        self.data.clear()
        self.log.append(("clear", None))

    async def update_data(self, **kwargs):
        self.data.update(kwargs)
        self.log.append(("update_data", kwargs))
        return dict(self.data)

    async def get_data(self):
        self.log.append(("get_data", None))
        return dict(self.data)


HOME_KYIV = ("home", "kyiv")
HOME_WARSAW = ("home", "warsaw")
HOME_ODESA = ("home", "odesa")
WORK_LVIV = ("work", "lviv")
GYM_WARSAW = ("gym", "warsaw")


@dataclass
class FakeShortcuts:
    home = HOME_KYIV
    work = WORK_LVIV

    @property
    def shortcuts(self):
        return [self.home, self.work]
