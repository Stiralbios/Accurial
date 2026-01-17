import uuid

from backend.database import Base
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserDO(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    questions = relationship("QuestionDO", back_populates="owner")
    predictions = relationship("PredictionDO", back_populates="owner")
    resolutions = relationship("ResolutionDO", back_populates="owner")
