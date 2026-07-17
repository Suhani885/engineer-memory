from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.github.webhook import router as github_webhook_router
from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_application() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.is_development else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            # Org-scoped API calls
            "X-Org-Slug",
            # GitHub webhook verification
            "X-Hub-Signature-256",
            "X-GitHub-Event",
            "X-GitHub-Delivery",
        ],
    )
    app.include_router(health_router)
    app.include_router(v1_router, prefix="/api/v1")
    # GitHub App webhook — intentionally outside /api/v1 (called by GitHub, not clients)
    app.include_router(github_webhook_router, prefix="/github")
    return app


app = create_application()

