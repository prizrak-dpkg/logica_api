from starlette.status import HTTP_409_CONFLICT

from fastapi.exceptions import HTTPException

from sqlalchemy import Column, String, func, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.product import ProductSchema


class ProductModel(TimeMixin, Base):
    __tablename__ = "product"

    gtin_producto = Column(BigInteger, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __str__(self):
        return self.name

    @classmethod
    async def get_by_gtin_producto(cls, gtin_producto: int):
        async with AsyncSession(db.engine) as session:
            statement = select(cls).filter_by(gtin_producto=gtin_producto)
            result = await session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def create_async(cls, item: ProductSchema):
        existing_item = await cls.get_by_gtin_producto(gtin_producto=item.gtin_producto)
        if existing_item:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=[
                    {
                        "field": "gtin_producto",
                        "msg": f"Ya existe una sucursal con el código {item.gtin_producto}",
                    }
                ],
            )
        new_item = cls(gtin_producto=item.gtin_producto, name=item.name)
        db.session.add(new_item)
        await commit_rollback()
        return new_item

    @classmethod
    async def get_count_async(cls):
        async with AsyncSession(db.engine) as session:
            statement = select(func.count()).select_from(cls)
            result = await session.execute(statement)
            return result.scalars().first()
