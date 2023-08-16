from pydantic import Field, BaseModel


class BranchSchema(BaseModel):
    gln_sucursal: int = Field(..., description="Código que identifica la sucursal")
    name: str = Field(..., description="Nombre de la sucursal")
