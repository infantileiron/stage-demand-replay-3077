import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.settings import settings
from src.utils.database import init_db
from src.middlewares.errors import ErrorMiddleware
from src.middlewares.audit import AuditMiddleware
from src.routes import auth,dataset,scenario,run,plan,report,schedule,health

@asynccontextmanager
async def lifespan(app):
    init_db()
    if settings.seed_demo:
        try:
            from scripts.seed_demo import seed
            seed()
        except Exception: logging.exception("Demo seed failed; server remains available")
    yield

app=FastAPI(title="拾光剧场 · 场次需求预演",version="1.0.0",lifespan=lifespan)
app.add_middleware(AuditMiddleware)
app.add_middleware(ErrorMiddleware)
for route in (auth,dataset,scenario,run,plan,report,schedule,health): app.include_router(route.router)
