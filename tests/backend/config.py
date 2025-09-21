import uuid6
from backend.database import Base
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import BaseFuzzyAttribute
from pydantic import BaseModel

from tests.backend.conftest import factory_session


class FuzzyUUID7(BaseFuzzyAttribute):
    def fuzz(self):
        return str(uuid6.uuid7())


class CustomSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    _schema_api_response: None | BaseModel = None

    class Meta:
        sqlalchemy_session = factory_session
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def to_api_response_data(cls, orm_model: Base | list[Base]):
        if cls._schema_api_response is None:
            raise NotImplementedError("Please setup _schema_api_response in your CustomSQLAlchemyModelFactory")
        if isinstance(orm_model, list):
            return [
                cls._schema_api_response.model_validate(item, strict=False, from_attributes=True).model_dump(
                    mode="json", by_alias=True
                )
                for item in orm_model
            ]
        return cls._schema_api_response.model_validate(orm_model, strict=False, from_attributes=True).model_dump(
            mode="json", by_alias=True
        )
