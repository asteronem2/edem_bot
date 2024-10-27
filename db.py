from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

DB_URL = 'sqlite+aiosqlite:///db.db'

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
