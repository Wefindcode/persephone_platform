from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .deps import init_db
from .errors import register_exception_handlers
from .instrumentation import instrumentator
from .logging import request_id_middleware, setup_logging
from .routers import auth, compute, deploy, monitor, prepare, runs, uploads
from .settings import settings


@asynccontextmanager
def lifespan(app: FastAPI):
    setup_logging()
    init_db()
    instrumentator.instrument(app).expose(app)
    yield


app = FastAPI(title="Persephone API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)

register_exception_handlers(app)


@app.get("/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse({"status": "ok"})


app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(compute.router)
app.include_router(prepare.router)
app.include_router(deploy.router)
app.include_router(runs.router)
app.include_router(monitor.router)
