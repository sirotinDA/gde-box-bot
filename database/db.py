from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Создание движка
engine = create_async_engine(DATABASE_URL, echo=False)

# Создание сессии
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
