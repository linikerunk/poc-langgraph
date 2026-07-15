import asyncio

from fastapi import APIRouter, HTTPException

from app.services.simulation import get_mode

router = APIRouter(prefix="/api", tags=["Mock API"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "mock-banking-api",
        "simulation_mode": get_mode(),
    }


@router.get("/products")
async def products():
    mode = get_mode()

    if mode == "slow":
        await asyncio.sleep(3.5)

    if mode == "error":
        raise HTTPException(
            status_code=503,
            detail="Simulated downstream database failure",
        )

    return [
        {"id": 1, "name": "Savings Account"},
        {"id": 2, "name": "Credit Card"},
        {"id": 3, "name": "Mortgage"},
    ]
