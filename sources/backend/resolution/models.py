import uuid
from datetime import datetime

import uuid6
from backend.database import Base
from backend.question.models import QuestionDO
from backend.user.models import UserDO
from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ResolutionDO(Base):
    __tablename__ = "resolution"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("question.id"), nullable=False, unique=True
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user.id"), nullable=False)

    owner: Mapped[UserDO] = relationship(back_populates="resolutions")
    question: Mapped[QuestionDO] = relationship(back_populates="resolution")
