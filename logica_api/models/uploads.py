from starlette.status import HTTP_409_CONFLICT, HTTP_404_NOT_FOUND

from fastapi.exceptions import HTTPException

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.uploads import UploadSchema
from logica_api.tasks.monitor import Status


class UploadsModel(TimeMixin, Base):
    __tablename__ = "uploads"

    name = Column(String, primary_key=True)
    folder = Column(String)
    status = Column(Integer)

    def __str__(self):
        return self.name

    @classmethod
    async def get_by_name(cls, name: int):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).filter_by(name=name)
            result = await session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def create_async(cls, item: UploadSchema):
        async with AsyncSession(db.engine) as session:
            existing_item = await cls.get_by_name(name=item.name)
            if existing_item:
                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail=[
                        {
                            "field": "name",
                            "msg": f"Ya existe una carga con el nombre {item.name}",
                        }
                    ],
                )
            new_item = cls(name=item.name, folder="-", status=Status.PENDIENTE.value)
            session.add(new_item)
            await commit_rollback(session)
            return new_item

    @classmethod
    async def change_state_async(cls, name: str, folder: str, status: Status):
        existing_item = await cls.get_by_name(name=name)
        if not existing_item:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=[
                    {
                        "field": "id",
                        "msg": f"El item que intenta actualizar no existe",
                    }
                ],
            )
        existing_item.folder = folder
        existing_item.status = status.value
        db.session.add(existing_item)
        await commit_rollback()
        return existing_item

    @classmethod
    async def get_latest_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).order_by(cls.created_at.desc()).limit(1)
            result = await session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def get_pending_uploads_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = (
                select(cls)
                .filter_by(status=Status.PENDIENTE.value)
                .order_by(cls.created_at.asc())
            )
            result = await session.execute(statement)
            return result.scalars().all()
