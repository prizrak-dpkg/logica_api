import asyncio
from enum import Enum

from logica_api.models.exceptionlog import ExceptionLogModel
from logica_api.schemas.uploads import UploadSchema
from logica_api.tasks.process_csv import process_csv_task


class Status(Enum):
    PENDIENTE = 1
    PROCESADO = 2
    EXCEPCION = 3


class MonitorUpload:
    @classmethod
    async def monitor_tasks(cls):
        from logica_api.models.uploads import UploadsModel

        while True:
            uploads = await UploadsModel.get_pending_uploads_async()
            if uploads:
                for upload in uploads:
                    try:
                        await process_csv_task(file_path=upload.name)
                    except Exception as e:
                        await ExceptionLogModel.register_exception(exception=e)
                        await UploadsModel.change_state_async(
                            name=upload.name, folder="*", status=Status.EXCEPCION
                        )
            else:
                print("No hay archivos pendientes por precesar")
            await asyncio.sleep(10)

    @classmethod
    async def put_file_on_hold(cls, upload_schema: UploadSchema):
        from logica_api.models.uploads import UploadsModel

        await UploadsModel.create_async(item=upload_schema)
