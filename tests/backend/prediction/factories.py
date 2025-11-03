from datetime import datetime, timezone

import factory
from backend.prediction.constants import PredictionStatus, PredictionType
from backend.prediction.models import PredictionDO
from backend.prediction.schemas import PredictionRead, PredictionValueBinary

from tests.backend.config import CustomSQLAlchemyModelFactory, FuzzyUUID7
from tests.backend.question.factories import QuestionFactory
from tests.backend.user.facories import UserFactory


class PredictionFactory(CustomSQLAlchemyModelFactory):
    _schema_api_response = PredictionRead

    class Meta:
        model = PredictionDO

    id = FuzzyUUID7()
    title = factory.Sequence(lambda n: f"Title {n}")
    description = factory.Sequence(lambda n: f"Description {n}")
    type = PredictionType.BINARY
    status = PredictionStatus.DRAFT
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    value = factory.LazyFunction(lambda: PredictionValueBinary(binary=True).model_dump())
    owner_id = factory.LazyAttribute(lambda o: o.owner.id if o.owner else None)
    question_id = factory.LazyAttribute(lambda o: o.question.id if o.question else None)

    owner = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QuestionFactory)
