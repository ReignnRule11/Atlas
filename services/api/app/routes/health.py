from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import engine

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "ok", "service": "atlas-api"}

@router.get("/ready")
def readiness():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}
