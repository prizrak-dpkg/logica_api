from datetime import date
from typing import List

from pydantic import Field, BaseModel


class InventorySchema(BaseModel):
    fecha_inventario: date = Field(
        ..., description="Fecha en la cual se toma el inventario del producto"
    )
    gln_cliente: int = Field(..., description="Código que identifica el cliente")
    gln_sucursal: int = Field(..., description="Código que identifica la sucursal")
    gtin_producto: int = Field(..., description="Código que identifica el producto")
    inventario_final: int = Field(..., description="Cantidad inventariada")
    precio_unidad: float = Field(..., description="Precio base de la Unidad")


class InventoryGetSchema(InventorySchema):
    id: int = Field(..., description="ID")


class PaginatedListSchema(BaseModel):
    total: int
    num_pages: int
    current_page: int
    per_page: int
    results: List[InventoryGetSchema]
