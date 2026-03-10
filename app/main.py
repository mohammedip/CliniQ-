from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import user, query
from app.api.routers import auth, queries, health
from app.services.mlflow_service import log_rag_config , init_mlflow
from app.core.exception_handlers import register_exception_handlers
from app.core.metrics import prometheus_middleware, metrics_router


app = FastAPI(
    title="CliniQ API",
    description="AI-powered medical platform",
    version="1.0.0"
)

# Middleware
app.middleware("http")(prometheus_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routers
app.include_router(auth.router)
app.include_router(queries.router)
app.include_router(health.router)
app.include_router(metrics_router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    init_mlflow()
    log_rag_config()