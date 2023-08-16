from datetime import datetime
import os
import shutil

import pandas as pd

from logica_api.models.exceptionlog import ExceptionLogModel
from logica_api.models.inventory import InventoryModel
from logica_api.schemas.inventory import InventorySchema


async def process_csv_task(file_path: str):
    from logica_api.tasks.monitor import Status
    from logica_api.models.uploads import UploadsModel

    status = Status.EXCEPCION
    folder = "Exception"
    try:
        upload_dir = os.path.join(os.getcwd(), "uploads")
        data = pd.read_csv(f"{upload_dir}/{file_path}")
        date_format = "%d/%m/%Y"
        change_flag = False
        current_customer = []
        for _, row in data.iterrows():
            try:
                current_gln_cliente = row["GLN_Cliente"]
                if len(current_customer) == 0:
                    current_customer.append(current_gln_cliente)
                else:
                    if not current_gln_cliente in current_customer:
                        change_flag = True
                fecha_inventario = datetime.strptime(
                    row["FechaInventario"], date_format
                )
                inventory_item = InventorySchema(
                    fecha_inventario=fecha_inventario.date(),
                    gln_cliente=current_gln_cliente,
                    gln_sucursal=row["GLN_Sucursal"],
                    gtin_producto=row["Gtin_Producto"],
                    inventario_final=row["Inventario_Final"],
                    precio_unidad=row["PrecioUnidad"],
                )
                await InventoryModel.create_async(inventory_item)
            except KeyError:
                raise
            except:
                continue
        folder = "several"
        status = Status.PROCESADO
        if not change_flag and len(current_customer) > 0:
            folder = f"{current_customer[0]}"
    except Exception as exception:
        await ExceptionLogModel.register_exception(exception=exception)
    finally:
        permanent_dir = os.path.join(upload_dir, folder)
        os.makedirs(permanent_dir, exist_ok=True)
        new_file_path = os.path.join(permanent_dir, file_path)
        shutil.move(f"{upload_dir}/{file_path}", new_file_path)
        await UploadsModel.change_state_async(
            name=file_path, folder=folder, status=status
        )
