from fastapi import APIRouter

from logica_api.schemas.inventory import PaginatedListSchema
from logica_api.services.inventory import InventoryRequest

router = APIRouter()


router.add_api_route(
    "/inventory",
    methods=["GET"],
    endpoint=InventoryRequest().get_paginated_data,
    response_model=PaginatedListSchema,
)

router.add_api_route(
    "/inventory",
    methods=["POST"],
    endpoint=InventoryRequest().upload_inventory_async,
)
