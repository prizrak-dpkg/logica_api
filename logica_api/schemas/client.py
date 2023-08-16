from pydantic import Field, BaseModel


class ClientSchema(BaseModel):
    gln_cliente: int = Field(..., description="Código que identifica el cliente")
    names: str = Field(..., description="Nombres del cliente")
    age: int = Field(..., description="Edad del cliente")
    phone: str = Field(..., description="Teléfono del cliente")
    email: str = Field(..., description="Correo del cliente")
