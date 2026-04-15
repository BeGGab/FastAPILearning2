import sqlalchemy as sa
from typing import List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs


from src_external.config import Settings

settings = Settings()


engine = create_async_engine(str(settings.postgres_url))
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

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


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
