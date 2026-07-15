from fastapi import FastAPI
from adapters.data_manager import InMemoryItemRepository
from adapters.http import create_item_router
from domain.services import ItemService

app = FastAPI(
    title="POC smoke API",
    description="Simple FastAPI app ",
    version="0.1.0",
)

repository = InMemoryItemRepository()
service = ItemService(repository=repository)
router = create_item_router(service)
app.include_router(router)

@app.get("/", summary="Health check")
def root() -> dict:
    return {
        "message": "POC smoke API is running",
        "endpoints": [
            "/api/items",
            "/api/items/common-names",
            "/api/items/{item_id}",
            "/api/test-logs/success",
            "/api/test-logs/error",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
