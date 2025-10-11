from enum import StrEnum, auto


class PredictionType(StrEnum):
    BINARY = auto()  # yes or no question


class QuestionStatus(StrEnum):
    DRAFT = auto()
    OPEN = auto()
    CLOSED = auto()
    ARCHIVED = auto()
