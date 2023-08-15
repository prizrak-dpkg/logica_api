from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.uploads import UploadSchema


class Uploads(TimeMixin, Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def __str__(self):
        return self.id

    @classmethod
    async def create_async(cls, item: UploadSchema):
        new_item = cls(
            name=item.name,
        )
        db.session.add(new_item)
        await commit_rollback()
        return new_item

    @classmethod
    async def get_latest_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).order_by(cls.created_at.desc()).limit(1)
            result = await session.execute(statement)
            return result.scalars().first()
