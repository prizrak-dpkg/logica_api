from datetime import date

from pydantic import Field, BaseModel


class InventorySchema(BaseModel):
    fecha_inventario: date = Field(
        ..., description="Fecha en la cual se toma el inventario del producto"
    )
    gln_cliente: str = Field(..., description="Código que identifica el Cliente")
    gln_sucursal: str = Field(..., description="Código que identifica la sucursal")
    gtin_producto: str = Field(..., description="Código que identifica el producto")
    inventario_final: int = Field(..., description=" Cantidad inventariada")
    precio_unidad: float = Field(..., description="Precio base de la Unidad")


class InventoryGetSchema(InventorySchema):
    id: int = Field(..., description="ID")
