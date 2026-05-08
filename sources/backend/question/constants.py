from enum import StrEnum, auto
from typing import Self

from backend.utils.status import StatusFSM


class QuestionStatus(StatusFSM, StrEnum):
    DRAFT = auto()
    OPEN = auto()
    CLOSED = auto()
    ARCHIVED = auto()

    @classmethod
    def _get_transitions(cls) -> dict[Self, list[Self]]:
        return {
            cls.DRAFT: [cls.OPEN],
            cls.OPEN: [cls.CLOSED, cls.ARCHIVED],
            cls.CLOSED: [cls.ARCHIVED],
            cls.ARCHIVED: [],
        }
