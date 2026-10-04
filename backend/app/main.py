from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.database import Base, SessionLocal, engine
from .core.logging_config import setup_logging
from .core.security import hash_password
from .api.routes import alerts, analytics, auth, inspections

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    from .models.user import User
    from .services.data_generator import ensure_seed_data

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(
                User(
                    email="admin@siteguard.com",
                    password_hash=hash_password("admin123"),
                    full_name="Demo Inspector",
                    role="inspector",
                )
            )
            db.commit()
            logger.info("Created default user")
        ensure_seed_data(db)
        logger.info("Seed data ready")
    finally:
        db.close()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health")
def health():
    return {"status": "healthy", "version": settings.VERSION}
