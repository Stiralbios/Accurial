from datetime import datetime, timezone

import factory
import uuid6
from backend.question.constants import QuestionStatus
from backend.resolution.models import ResolutionDO
from backend.resolution.schemas import ResolutionRead

from tests.backend.config import CustomSQLAlchemyModelFactory
from tests.backend.question.factories import QuestionFactory
from tests.backend.user.facories import UserFactory


class ResolutionFactory(CustomSQLAlchemyModelFactory):
    _schema_api_response = ResolutionRead

    class Meta:
        model = ResolutionDO

    id = factory.LazyAttribute(lambda o: uuid6.uuid7())
    date = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    value = "true"
    description = "Test resolution description"
    owner_id = factory.LazyAttribute(lambda o: o.owner.id if o.owner else None)
    question_id = factory.LazyAttribute(lambda o: o.question.id if o.question else None)

    owner = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QuestionFactory, status=QuestionStatus.OPEN)
