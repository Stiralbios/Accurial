import factory
from backend.question.constants import PredictionType, QuestionStatus
from backend.question.models import QuestionDO
from backend.question.schemas import QuestionRead

from tests.backend.config import CustomSQLAlchemyModelFactory, FuzzyUUID7
from tests.backend.user.facories import UserFactory


class QuestionFactory(CustomSQLAlchemyModelFactory):
    _schema_api_response = QuestionRead

    class Meta:
        model = QuestionDO

    id = FuzzyUUID7()
    title = factory.Sequence(lambda n: f"Title {n}")
    description = factory.Sequence(lambda n: f"Description {n}")
    prediction_type = PredictionType.BINARY
    status = QuestionStatus.DRAFT
    owner_id = factory.LazyAttribute(lambda o: o.owner.id if o.owner else None)

    owner = factory.SubFactory(UserFactory)
