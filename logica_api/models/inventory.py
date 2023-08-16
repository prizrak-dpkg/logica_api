import math
from typing import List, Tuple
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
    BigInteger,
    func,
    select,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.inventory import (
    InventoryGetSchema,
    InventorySchema,
    PaginatedListSchema,
)


class InventoryModel(TimeMixin, Base):
    __tablename__ = "inventory"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fecha_inventario = Column(Date)
    gln_cliente = Column(BigInteger, ForeignKey("client.gln_cliente"))
    gln_sucursal = Column(BigInteger, ForeignKey("branch.gln_sucursal"))
    gtin_producto = Column(BigInteger, ForeignKey("product.gtin_producto"))
    inventario_final = Column(Integer)
    precio_unidad = Column(Float)

    branch = relationship("BranchModel")
    client = relationship("ClientModel")
    product = relationship("ProductModel")

    __table_args__ = (
        UniqueConstraint(
            "fecha_inventario", "gln_cliente", "gln_sucursal", "gtin_producto"
        ),
    )

    def __str__(self):
        return self.gtin_producto

    @classmethod
    async def create_async(cls, item: InventorySchema):
        new_item = cls(
            fecha_inventario=item.fecha_inventario,
            gln_cliente=item.gln_cliente,
            gln_sucursal=item.gln_sucursal,
            gtin_producto=item.gtin_producto,
            inventario_final=item.inventario_final,
            precio_unidad=item.precio_unidad,
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

    @classmethod
    async def get_paginate_async(cls, limit: int, page: int):
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        if page <= 0:
            page = 1
        offset = (page - 1) * limit
        async with AsyncSession(db.engine) as session:
            statement = select(cls).limit(limit).offset(offset)
            result = await session.execute(statement)
            total = await cls.get_count_async()
            return cls._get_paginated_response(
                total, offset, limit, result.scalars().all()
            )

    @classmethod
    def _get_paginated_response(
        cls, total: int, skip: int, limit: int, results: List["InventoryModel"]
    ):
        num_pages = math.ceil(total / limit)
        current_page = int(skip / limit) + 1
        return PaginatedListSchema(
            total=total,
            num_pages=num_pages,
            current_page=current_page,
            per_page=limit,
            results=list(
                map(
                    lambda x: InventoryGetSchema(
                        fecha_inventario=x.fecha_inventario,
                        gln_cliente=x.gln_cliente,
                        gln_sucursal=x.gln_sucursal,
                        gtin_producto=x.gtin_producto,
                        inventario_final=x.inventario_final,
                        precio_unidad=x.precio_unidad,
                        id=x.id,
                    ),
                    results,
                )
            ),
        )
