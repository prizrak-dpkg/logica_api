from pydantic import Field, BaseModel


class UploadSchema(BaseModel):
    name: str = Field(..., description="Nombre del archivo")
