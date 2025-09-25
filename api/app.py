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
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic model for input (so created_at and id are not sent by client)
class ItemCreate(BaseSettings):
    name: str
    description: Optional[str] = None
    price: float

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="FastAPI PostgreSQL Async Example")

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
@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: dict, session: AsyncSession = Depends(get_session)):
    """Recebe um dict com keys: name, description (opcional), price
       Exemplo de body JSON:
       {
         "name": "Bola",
         "description": "Bola de futebol",
         "price": 49.9
       }
    """
    # validação básica manual (poderia usar Pydantic model)
    if "name" not in item or "price" not in item:
        raise HTTPException(status_code=400, detail="Campos 'name' e 'price' são obrigatórios")

    new_item = Item(name=item.get("name"), description=item.get("description"), price=float(item.get("price")))

    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)

    return new_item

# Endpoint opcional: listar itens
@app.get("/items")
async def list_items(limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT * FROM item LIMIT :limit").bindparams(limit=limit))
    rows = result.fetchall()
    # converter rows para dicts simples
    items = {}
    for row in rows:
        items[row.id] = {"name": row.name, "description": row.description, "price": row.price, "created_at": row.created_at}
    return {"count": len(items), "items": items}
