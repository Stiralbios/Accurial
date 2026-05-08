from backend.prediction.constants import PredictionStatus


async def test_prediction_can_transition_to_valid():
    assert PredictionStatus.can_transition_to(PredictionStatus.DRAFT, PredictionStatus.PUBLISHED) is True
    assert PredictionStatus.can_transition_to(PredictionStatus.PUBLISHED, PredictionStatus.CLOSED) is True


async def test_prediction_can_transition_to_invalid():
    assert PredictionStatus.can_transition_to(PredictionStatus.DRAFT, PredictionStatus.CLOSED) is False
    assert PredictionStatus.can_transition_to(PredictionStatus.CLOSED, PredictionStatus.PUBLISHED) is False
    assert PredictionStatus.can_transition_to(PredictionStatus.PUBLISHED, PredictionStatus.DRAFT) is False


async def test_prediction_get_valid_transitions():
    assert PredictionStatus.get_valid_transitions(PredictionStatus.DRAFT) == [PredictionStatus.PUBLISHED]
    assert PredictionStatus.get_valid_transitions(PredictionStatus.PUBLISHED) == [PredictionStatus.CLOSED]
    assert PredictionStatus.get_valid_transitions(PredictionStatus.CLOSED) == []
