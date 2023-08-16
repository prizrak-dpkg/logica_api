import os
import shutil

from starlette.status import HTTP_409_CONFLICT

from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from logica_api.models.exceptionlog import ExceptionLogModel
from logica_api.models.inventory import InventoryModel

from logica_api.schemas.uploads import UploadSchema
from logica_api.tasks.monitor import MonitorUpload


class InventoryRequest:
    async def upload_inventory_async(
        self,
        file: UploadFile = File(...),
    ):
        try:
            random_bytes = os.urandom(16)
            random_hash = "".join(f"{byte:02x}" for byte in random_bytes)
            upload_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            name = f"temp_{random_hash}_{file.filename}"
            temp_file_path = f"{upload_dir}/{name}"
            with open(temp_file_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
            upload_schema = UploadSchema(name=name)
            await MonitorUpload.put_file_on_hold(upload_schema)
            return JSONResponse(
                content={"message": "Archivo recibido y proceso asincrónico iniciado"}
            )
        except Exception as exception:
            await ExceptionLogModel.register_exception(exception=exception)
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=[
                    {
                        "field": "unexpected",
                        "msg": "Ha ocurrido un error procesando el archivo",
                    }
                ],
            )

    async def get_paginated_data(self, limit: int = 10, page: int = 1):
        return await InventoryModel.get_paginate_async(limit, page)
