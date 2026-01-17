import uuid

import uuid6
from backend.database import Base
from backend.user.models import UserDO
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


class QuestionDO(Base):
    __tablename__ = "question"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String())
    prediction_type: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user.id"), nullable=False)

    owner: Mapped[UserDO] = relationship(back_populates="questions")
    predictions = relationship("PredictionDO", back_populates="question")
    resolution = relationship("ResolutionDO", back_populates="question", uselist=False)
