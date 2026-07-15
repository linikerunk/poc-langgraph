from fastapi import APIRouter

from app.services.simulation import get_mode, set_mode

router = APIRouter(prefix="/api/admin", tags=["Simulation"])


@router.post("/simulation/{mode}")
def update_simulation(mode: str):
    current = set_mode(mode.lower())
    return {"simulation_mode": current}


@router.get("/simulation")
def current_simulation():
    return {"simulation_mode": get_mode()}
