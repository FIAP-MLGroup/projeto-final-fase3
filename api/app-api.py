from typing import Optional
from datetime import datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# ----------------------
# Config
# ----------------------
class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

DATABASE_URL = settings.DATABASE_URL

# Async engine & session
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# ----------------------
# Models
# ----------------------
class MedicaoRadar(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    placa: str
    latitude: float
    longitude: float
    velocidade: float
    timestamp_deteccao: datetime = Field(default_factory=datetime.utcnow)

# Pydantic model for input (so created_at and id are not sent by client)
class MedicaoRadarCreate(BaseSettings):
    placa: str
    latitude: float
    longitude: float
    velocidade: float
    timestamp_deteccao: datetime = Field(default_factory=datetime.utcnow)

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="Medições de Radar API", version="1.0.0")

# Startup event to create tables
@app.on_event("startup")
async def on_startup():
    # create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency to get async session
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Simple health check
@app.get("/healthz")
async def health():
    return {"status": "ok"}

# Create item endpoint
@app.post("/medicoes", status_code=status.HTTP_201_CREATED)
async def create_item(medicaoRadar: dict, session: AsyncSession = Depends(get_session)):
    """Recebe um dict com keys: placa, latitude, longitude, velocidade e timestamp_deteccao
        e insere no banco de dados.
        Exemplo de body JSON:
        {
            "placa": "QNA3053",
            "latitude": -22.9537020000,
            "longitude": -43.3757780000,
            "velocidade": 20,
            "timestamp_deteccao": "2025-07-23 09:11"
        }
    """

    novaMedicaoRadar = MedicaoRadar(placa=medicaoRadar.get("placa"), 
                            latitude=medicaoRadar.get("latitude"), 
                            longitude=medicaoRadar.get("longitude"), 
                            velocidade=medicaoRadar.get("velocidade"), 
                            timestamp_deteccao=datetime.strptime(medicaoRadar.get("timestamp_deteccao", datetime.utcnow()), "%Y-%m-%d %H:%M"))

    session.add(novaMedicaoRadar)
    await session.commit()
    await session.refresh(novaMedicaoRadar)

    return novaMedicaoRadar

# Endpoint opcional: listar itens
@app.get("/medicoes")
async def list_items(limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT * FROM MedicaoRadar LIMIT :limit").bindparams(limit=limit))
    rows = result.fetchall()
    # converter rows para dicts simples
    medicoes = {}
    for row in rows:
        medicoes[row.id] = {
            "placa": row.placa,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "velocidade": row.velocidade,
            "timestamp_deteccao": row.timestamp_deteccao.isoformat()
        }
    return {"count": len(medicoes), "items": medicoes}
