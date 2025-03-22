from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/")
async def create_project() -> None:
    pass
