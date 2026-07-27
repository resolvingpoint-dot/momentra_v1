from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, me, app as app_router, moments, my_money, group, group_app, group_shared, group_read, group_settlements, group_trips, business, business_app, business_active, circle, life360, memory, personal, invites, health, reference_data, metadata, debug
from app.api import local_uploads
import app.core.base  # noqa: F401  # register the full ORM model registry so cross-domain mappers resolve
from app.core.config import settings
from app.core.database import dispose_engine
from app.core.exceptions import register_exception_handlers
from app.core.firebase import init_firebase
from app.core.logging import configure_logging
from app.core.observability import observability_middleware
from app.core.rate_limit import add_rate_limiting

configure_logging(settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging(settings.debug)
    init_firebase()
    from app.domains.moment_engine import register_default_domains, register_moment_handlers
    from app.domains.personal.life_operations.quick_add.handlers import (
        register_quick_add_handlers,
    )
    from app.domains.personal.templates import register_template_projection_handlers
    from app.domains.projections.handlers import register_projection_handlers
    from app.shared.events.audit import register_event_audit

    register_default_domains()
    register_moment_handlers()
    register_quick_add_handlers()
    register_template_projection_handlers()
    register_projection_handlers()
    register_event_audit()
    # Startup stays non-blocking: we only report configuration here. Live DB
    # connectivity is verified on-demand via the /health/ready probe.
    if settings.database_url:
        logger.info("Database configured")
    else:
        logger.warning("DATABASE_URL not configured — DB-backed endpoints will fail")
    logger.info("Momentra API started (debug=%s)", settings.debug)
    yield
    await dispose_engine()
    logger.info("Momentra API shutdown complete")


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

register_exception_handlers(app)


@app.middleware("http")
async def _observability(request, call_next):
    return await observability_middleware(request, call_next)


@app.middleware("http")
async def log_origin(request, call_next):
    origin = request.headers.get("origin")
    if origin:
        logger.info("Request origin: %s %s %s", request.method, request.url.path, origin)
    return await call_next(request)


if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if not settings.debug:
    add_rate_limiting(
        app,
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

app.include_router(auth.router, prefix="/api/v1")
app.include_router(me.router, prefix="/api/v1")
app.include_router(app_router.router, prefix="/api/v1")
app.include_router(reference_data.router, prefix="/api/v1")
app.include_router(metadata.router, prefix="/api/v1")
app.include_router(invites.router, prefix="/api/v1")
app.include_router(moments.router, prefix="/api/v1")
app.include_router(my_money.router, prefix="/api/v1")
app.include_router(group_app.router, prefix="/api/v1")
app.include_router(group_settlements.router, prefix="/api/v1")
app.include_router(group_shared.router, prefix="/api/v1")
app.include_router(group_read.router, prefix="/api/v1")
app.include_router(group_trips.router, prefix="/api/v1")
app.include_router(group_trips.options_router, prefix="/api/v1")
app.include_router(group.router, prefix="/api/v1")
app.include_router(business_app.router, prefix="/api/v1")
app.include_router(business_active.router, prefix="/api/v1")
app.include_router(business.router, prefix="/api/v1")
app.include_router(circle.router, prefix="/api/v1")
app.include_router(life360.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")
app.include_router(personal.router, prefix="/api/v1")
app.include_router(debug.router, prefix="/api/v1")
# Health probes are mounted at the app root (no /api/v1 prefix) so infra probes
# and the rate-limit exclusion list keep hitting stable /health paths.
app.include_router(health.router)
# Stub signed-upload target when STORAGE_PUBLIC_BASE_URL is unset.
app.include_router(local_uploads.router)
