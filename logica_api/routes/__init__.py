from fastapi import APIRouter

from logica_api.routes.inventory import router as inventory_router

router = APIRouter()

router.include_router(inventory_router, tags=["Inventory"])
