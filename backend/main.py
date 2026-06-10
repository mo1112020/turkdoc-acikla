from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import sys

from backend.config import (
    CORS_ORIGINS,
    IS_PRODUCTION,
    UPLOAD_DIR,
    config_status,
    validate_settings,
)
from backend.database import Base, engine
from backend.middleware import SecurityHeadersMiddleware
from backend.routes import auth, documents

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        validate_settings()
    except RuntimeError as exc:
        # Don't block the server from starting — Railway healthcheck needs /health.
        print(f"Startup warning: {exc}", file=sys.stderr)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="turkdoc API",
    description="Explain Turkish government documents — upload, store, and understand.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

app.add_middleware(SecurityHeadersMiddleware)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(auth.router)
app.include_router(documents.router)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    detail = "An internal error occurred." if IS_PRODUCTION else str(exc)
    return JSONResponse(status_code=500, content={"detail": detail})


@app.get("/")
def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "turkdoc API is running. Visit /docs for API documentation."}


@app.get("/health")
def health():
    status = config_status()
    return {
        "status": "ok" if status["ready"] else "degraded",
        "environment": "production" if IS_PRODUCTION else "development",
        "ready": status["ready"],
        "missing": status["missing"],
    }
