from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logica_api.config import commit_rollback, db, Base
from logica_api.models.mixins import TimeMixin
from logica_api.schemas.inventory import InventorySchema


class Inventory(TimeMixin, Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_inventario = Column(Date)
    gln_cliente = Column(String)
    gln_sucursal = Column(String)
    gtin_producto = Column(String)
    inventario_final = Column(Integer)
    precio_unidad = Column(Float)

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
