from pydantic import Field, BaseModel


class ExceptionSchema(BaseModel):
    description: str = Field(..., description="Descripción de la excepción")
