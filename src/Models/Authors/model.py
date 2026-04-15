import sqlalchemy as sa
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from src.models.core.db import Base

metadata = sa.MetaData()


class BiographyAuthor(Base):
    __tablename__ = "biographies_authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID]
    text: Mapped[str] = mapped_column(sa.Text)
    year_of_birth: Mapped[int]
    year_of_death: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.now, nullable=True
    )

