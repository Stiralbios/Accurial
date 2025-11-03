import uuid
from datetime import datetime

import uuid6
from backend.database import Base
from backend.question.models import QuestionDO
from backend.user.models import UserDO
from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PredictionDO(Base):
    __tablename__ = "prediction"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String())
    type: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    value: Mapped[dict] = mapped_column(JSONB)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("question.id"), nullable=False)

    owner: Mapped[UserDO] = relationship(back_populates="predictions")
    question: Mapped[QuestionDO] = relationship(back_populates="predictions")
