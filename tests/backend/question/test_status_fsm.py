from backend.question.constants import QuestionStatus


async def test_question_can_transition_to_valid():
    assert QuestionStatus.can_transition_to(QuestionStatus.DRAFT, QuestionStatus.OPEN) is True
    assert QuestionStatus.can_transition_to(QuestionStatus.OPEN, QuestionStatus.CLOSED) is True
    assert QuestionStatus.can_transition_to(QuestionStatus.OPEN, QuestionStatus.ARCHIVED) is True
    assert QuestionStatus.can_transition_to(QuestionStatus.CLOSED, QuestionStatus.ARCHIVED) is True


async def test_question_can_transition_to_invalid():
    assert QuestionStatus.can_transition_to(QuestionStatus.OPEN, QuestionStatus.DRAFT) is False
    assert QuestionStatus.can_transition_to(QuestionStatus.CLOSED, QuestionStatus.OPEN) is False
    assert QuestionStatus.can_transition_to(QuestionStatus.ARCHIVED, QuestionStatus.DRAFT) is False
    assert QuestionStatus.can_transition_to(QuestionStatus.DRAFT, QuestionStatus.CLOSED) is False


async def test_question_get_valid_transitions():
    assert QuestionStatus.get_valid_transitions(QuestionStatus.DRAFT) == [QuestionStatus.OPEN]
    assert set(QuestionStatus.get_valid_transitions(QuestionStatus.OPEN)) == {
        QuestionStatus.CLOSED,
        QuestionStatus.ARCHIVED,
    }
    assert QuestionStatus.get_valid_transitions(QuestionStatus.CLOSED) == [QuestionStatus.ARCHIVED]
    assert QuestionStatus.get_valid_transitions(QuestionStatus.ARCHIVED) == []
