from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import attachments, health, tickets, webhooks
from .config import get_settings
from .database import create_all

settings = get_settings()


def create_app() -> FastAPI:
    create_all()
    app = FastAPI(title=settings.app_name, description=settings.description)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(attachments.router)
    app.include_router(tickets.router)
    app.include_router(webhooks.router)

    return app


app = create_app()
