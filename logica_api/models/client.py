from starlette.status import HTTP_409_CONFLICT

from fastapi.exceptions import HTTPException

from sqlalchemy import Column, Integer, String, func, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.client import ClientSchema


class ClientModel(TimeMixin, Base):
    __tablename__ = "client"

    gln_cliente = Column(BigInteger, primary_key=True)
    names = Column(String)
    age = Column(Integer)
    phone = Column(String)
    email = Column(String)

    def __str__(self):
        return self.names

    @classmethod
    async def get_by_gln_cliente(cls, gln_cliente: int):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).filter_by(gln_cliente=gln_cliente)
            result = await session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def create_async(cls, item: ClientSchema):
        existing_item = await cls.get_by_gln_cliente(gln_cliente=item.gln_cliente)
        if existing_item:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=[
                    {
                        "field": "gln_cliente",
                        "msg": f"Ya existe un cliente con el código {item.gln_cliente}",
                    }
                ],
            )
        new_item = cls(
            gln_cliente=item.gln_cliente,
            names=item.names,
            age=item.age,
            phone=item.phone,
            email=item.email,
        )
        db.session.add(new_item)
        await commit_rollback()
        return new_item

    @classmethod
    async def get_count_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = select(func.count()).select_from(cls)
            result = await session.execute(statement)
            return result.scalars().first()
