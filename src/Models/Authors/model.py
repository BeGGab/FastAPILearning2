import sqlalchemy as sa
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import class_mapper, declarative_base, DeclarativeMeta


metadata = sa.MetaData()

class BaseServiceModel(AsyncAttrs):
    __abstract__ = True

    @classmethod
    def on_conflict_constrauuid(cls) -> tuple | None:
        return None

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}

Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)

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

