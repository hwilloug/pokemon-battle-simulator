from fastapi import APIRouter

router = APIRouter(
    prefix="/status",
    tags=["status"]
)

@router.get("/{id}")
async def get_status(id: str):
    return {"status": f"Battle {id} status"}
