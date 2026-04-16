"""
Configuración de la base de datos — PostgreSQL + SQLAlchemy 2.x
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from app.config import settings

# Pool optimizado para PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # Verifica conexiones antes de usarlas
    pool_recycle=3600,        # Recicla conexiones cada hora
    echo=(settings.APP_ENV == "development"),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Dependencia FastAPI: sesión de base de datos con cierre garantizado."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifica que la base de datos esté disponible."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
