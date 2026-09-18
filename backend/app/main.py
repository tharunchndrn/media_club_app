import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import committee, events, suggestions
from app.schemas.health import HealthResponse

app = FastAPI(title="NIBM KIC Media Club API", version="0.1.0")

# Allow all dev origins including dynamic Flutter web ports (localhost:XXXXX)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cross_origin_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

class CORSStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        return resp

# Mount images static directory with CORS headers if it exists
images_dir = Path(__file__).resolve().parent.parent.parent / "admin" / "public" / "images"
if images_dir.exists():
    app.mount("/images", CORSStaticFiles(directory=str(images_dir)), name="images")

app.include_router(events.router, prefix="/api/v1")
app.include_router(committee.router, prefix="/api/v1")
app.include_router(suggestions.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")

