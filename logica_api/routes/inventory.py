from fastapi import APIRouter

from logica_api.services.inventory import InventoryRequest

router = APIRouter()


router.add_api_route(
    "/inventory",
    methods=["POST"],
    endpoint=InventoryRequest().upload_inventory_async,
)
