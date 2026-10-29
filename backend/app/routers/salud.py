from fastapi import APIRouter

router = APIRouter(tags=["Sistema"])

@router.get("/salud")
def salud():
    return {"estado": "ok"}