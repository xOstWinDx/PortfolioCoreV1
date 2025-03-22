from fastapi import FastAPI
from src.presentation.http.projects.router import router as projects_router

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog.",
)

app.include_router(projects_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}
