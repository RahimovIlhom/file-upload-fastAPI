from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from environs import Env

env = Env()
env.read_env()

user = env("POSTGRES_USER")
password = env("POSTGRES_PASSWORD")
dbname = env("POSTGRES_DB")
host = env("POSTGRES_HOST")
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{dbname}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
        await db.commit()
