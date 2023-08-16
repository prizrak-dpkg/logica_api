from starlette.status import HTTP_409_CONFLICT

from fastapi.exceptions import HTTPException

from sqlalchemy import Column, BigInteger, String, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.branch import BranchSchema


class BranchModel(TimeMixin, Base):
    __tablename__ = "branch"

    gln_sucursal = Column(BigInteger, primary_key=True)
    name = Column(String)

    def __str__(self):
        return self.name

    @classmethod
    async def get_by_gln_sucursal(cls, gln_sucursal: int):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).filter_by(gln_sucursal=gln_sucursal)
            result = await session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def create_async(cls, item: BranchSchema):
        existing_item = await cls.get_by_gln_sucursal(gln_sucursal=item.gln_sucursal)
        if existing_item:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=[
                    {
                        "field": "gln_sucursal",
                        "msg": f"Ya existe una sucursal con el código {item.gln_sucursal}",
                    }
                ],
            )
        new_item = cls(gln_sucursal=item.gln_sucursal, name=item.name)
        db.session.add(new_item)
        await commit_rollback()
        return new_item

    @classmethod
    async def get_count_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = select(func.count()).select_from(cls)
            result = await session.execute(statement)
            return result.scalars().first()
