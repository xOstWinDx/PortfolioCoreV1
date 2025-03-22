from fastapi import FastAPI

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog."
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}