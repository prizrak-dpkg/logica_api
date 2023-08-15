from datetime import date, datetime
import asyncio
import json
import os
import shutil
import traceback

from fastapi import File, UploadFile
from fastapi.responses import JSONResponse

import pandas as pd

from logica_api.models.exceptionlog import ExceptionLog
from logica_api.models.inventory import Inventory
from logica_api.models.uploads import Uploads
from logica_api.schemas.exceptionlog import ExceptionSchema
from logica_api.schemas.inventory import InventorySchema
from logica_api.schemas.uploads import UploadSchema


class InventoryRequest:
    async def process_csv(self, file_path: str):
        try:
            data = pd.read_csv(file_path)
            date_format = "%d/%m/%Y"
            for _, row in data.iterrows():
                fecha_inevntario = datetime.strptime(
                    row["FechaInventario"], date_format
                )
                inventory_item = InventorySchema(
                    fecha_inventario=fecha_inevntario.date(),
                    gln_cliente="{}".format(row["GLN_Cliente"]),
                    gln_sucursal="{}".format(row["GLN_Sucrusal"]),
                    gtin_producto="{}".format(row["Gtin_Producto"]),
                    inventario_final=row["Inventario_Final"],
                    precio_unidad=row["PrecioUnidad"],
                )
                await Inventory.create_async(inventory_item)
        except Exception as exception:
            exception_info = {
                "error_type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc(),
            }
            json_data = json.dumps(exception_info)
            exception_schema = ExceptionSchema(
                description=f"Error processing CSV: {json_data}"
            )
            await ExceptionLog.create_async(exception_schema)

    async def upload_inventory_async(
        self,
        file: UploadFile = File(...),
    ):
        try:
            random_bytes = os.urandom(16)
            random_hash = "".join(f"{byte:02x}" for byte in random_bytes)
            upload_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            name = f"temp_{file.filename}_{random_hash}"
            temp_file_path = f"{upload_dir}/{name}"
            with open(temp_file_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)

            upload_schema = UploadSchema(name=name)
            await Uploads.create_async(upload_schema)

            asyncio.create_task(self.process_csv(temp_file_path))

            return JSONResponse(
                content={"message": "Archivo recibido y proceso asincrónico iniciado"}
            )
        finally:
            ...
