from enum import StrEnum, auto


class PredictionType(StrEnum):
    BINARY = auto()  # yes or no question/prediction


class PredictionStatus(StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    CLOSED = auto()
