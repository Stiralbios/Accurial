from enum import StrEnum, auto


class PredictionType(StrEnum):
    BINARY = auto()


class QuestionStatus(StrEnum):
    DRAFT = auto()
    OPEN = auto()
    CLOSED = auto()
    ARCHIVED = auto()
