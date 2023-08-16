from pydantic import Field, BaseModel


class ProductSchema(BaseModel):
    gtin_producto: int = Field(..., description="Código que identifica el producto")
    name: str = Field(..., description="Nombre del producto")
    description: str = Field(..., description="Descripción del producto")
