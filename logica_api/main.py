import asyncio
import uvicorn

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data import InitialData

from logica_api import routers
from logica_api.config import db, get_settings
from logica_api.tasks.monitor import MonitorUpload

is_production = False


def init_api() -> FastAPI:
    """
    Inicializa la aplicación FastAPI.

    Returns:
        FastAPI: Instancia inicializada de la aplicación FastAPI.
    """
    db.init()

    api = FastAPI(
        title="Logica API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        debug=False,
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().ORIGINS.split(","),
        allow_credentials=False,
        allow_methods=("GET", "POST"),
        allow_headers=("Content-Type", "Authorization", "Host", "User-Agent"),
    )

    @api.on_event("startup")
    async def startup():
        """
        Función de devolución de llamada para el evento de inicio.
        """
        await db.create_all()
        initial_data = InitialData()
        await initial_data.upload_data_async()
        asyncio.create_task(MonitorUpload.monitor_tasks())
        for router in routers:
            api.include_router(router, prefix="/api")
        if not is_production:
            # Se Importan y configuran los módulos de documentación si no estamos en ambiente de producción (Swagger y ReDoc)
            from fastapi import APIRouter
            from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
            from fastapi.openapi.utils import get_openapi

            router = APIRouter()

            @router.get("/docs", include_in_schema=False)
            async def custom_swagger_ui_html():
                return get_swagger_ui_html(
                    openapi_url="/openapi.json", title=api.title + " - Swagger UI"
                )

            @router.get("/redoc", include_in_schema=False)
            async def redoc_html():
                return get_redoc_html(
                    openapi_url="/openapi.json", title=api.title + " - ReDoc"
                )

            @router.get("/openapi.json", include_in_schema=False)
            async def openapi_endpoint():
                return get_openapi(
                    title=api.title,
                    version=api.version,
                    routes=api.routes,
                )

            api.include_router(router)

    @api.on_event("shutdown")
    async def shutdown():
        """
        Función de devolución de llamada para el evento de apagado.
        """
        await db.session.close()

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = []
        for error in exc.errors():
            errors.append({"field": error["loc"][1], "msg": error["msg"]})
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )

    return api


logica_api = init_api()


def start():
    """
    Inicia el servidor Uvicorn para ejecutar la instancia de FastAPI.
    """
    uvicorn.run("logica_api.main:logica_api", host="0.0.0.0", port=8888, reload=False)
