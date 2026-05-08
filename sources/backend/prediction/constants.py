from enum import StrEnum, auto
from typing import Self

from backend.utils.status import StatusFSM


class PredictionType(StrEnum):
    BINARY = auto()  # yes or no question/prediction


class PredictionStatus(StatusFSM, StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    CLOSED = auto()

    @classmethod
    def _get_transitions(cls) -> dict[Self, list[Self]]:
        return {cls.DRAFT: [cls.PUBLISHED], cls.PUBLISHED: [cls.CLOSED], cls.CLOSED: []}
