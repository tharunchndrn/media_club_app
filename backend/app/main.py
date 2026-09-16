from fastapi import FastAPI

from app.schemas.health import HealthResponse

app = FastAPI(title="Studio 006 API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
