import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import router
from app.security.budget_controller import (
    configure_budget_controller,
    BudgetConfig,
)
from app.security.content_filter import get_content_filter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("langgraph").setLevel(logging.WARNING)

    configure_budget_controller(BudgetConfig(
        max_daily_cost=settings.max_daily_cost,
        max_session_cost=settings.max_session_cost,
        max_tokens_per_session=settings.max_tokens_per_session,
        max_requests_per_minute=settings.max_requests_per_minute,
        hard_stop_enabled=settings.hard_stop_enabled,
        alert_at_percentage=settings.budget_alert_percentage,
    ))

    from app.db.seed import seed_data
    try:
        await seed_data()
        logging.info("Database initialized & seeded successfully.")
    except Exception as e:
        logging.warning("Database seed skipped or failed: %s", str(e))

    from app.graph.graph import get_graph
    get_graph()

    logging.info("E-commerce agent ready — budget: $%.2f/day", settings.max_daily_cost)
    yield
    # ---- shutdown ----
    logging.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aisle",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
