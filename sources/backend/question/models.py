import uuid

import uuid6
from backend.database import Base
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

# todo add user


class QuestionDO(Base):
    __tablename__ = "question"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid6.uuid7)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String())  # todo check the len
    prediction_type: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
