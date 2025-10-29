from enum import StrEnum, auto


class PredictionType(StrEnum):
    BINARY = auto()  # yes or no question/prediction


class PredictionStatus(StrEnum):
    DRAFT = auto()
    CREATED = auto()
    CLOSED = auto()
