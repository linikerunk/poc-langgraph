import logging

from fastapi import APIRouter, HTTPException
from typing import List

from domain.dtos import CreateItemDTO, ItemDTO
from domain.services import ItemService

logger = logging.getLogger(__name__)


def create_item_router(service: ItemService) -> APIRouter:
    router = APIRouter(prefix="", tags=["items", "logs"])

    @router.post("/", response_model=ItemDTO, summary="Create an item")
    def create_item(payload: CreateItemDTO) -> ItemDTO:
        try:
            return service.create_item(payload)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))

    @router.get("/", response_model=List[ItemDTO], summary="List items")
    def list_items() -> List[ItemDTO]:
        return service.list_items()

    @router.get("/test-logs/success", summary="Test a successful log entry")
    def test_logs_success() -> dict:
        logger.info("Log test success endpoint was called")
        return {"status": "success", "message": "Log test successful"}

    @router.get("/test-logs/error", summary="Test an error log entry")
    def test_logs_error() -> dict:
        logger.error("Log test error endpoint was called")
        raise HTTPException(status_code=500, detail="Test error occurred")

    @router.get("/common-names", response_model=List[str], summary="List common names")
    def common_names() -> List[str]:
        return service.get_common_names()

    @router.get("/{item_id}", response_model=ItemDTO, summary="Get item by ID")
    def get_item(item_id: int) -> ItemDTO:
        try:
            return service.get_item(item_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error))

    return router
