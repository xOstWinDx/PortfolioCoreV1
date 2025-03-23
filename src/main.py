from fastapi import FastAPI
from src.presentation.http.projects.router import router as projects_router
from src.presentation.http.auth.router import router as auth_router

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog.",
)

app.include_router(projects_router)
app.include_router(auth_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}
