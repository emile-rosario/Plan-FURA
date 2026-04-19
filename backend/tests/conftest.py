"""
Configuración de tests — SQLite en memoria, sin lifespan PostgreSQL.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Base de datos SQLite para tests ───────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_funeraria.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Importar DESPUÉS de configurar el engine
from app.database import Base, get_db  # noqa: E402
from app.main import app              # noqa: E402


def override_get_db():
    """Sustituye la sesión PostgreSQL por una SQLite en tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea las tablas en SQLite antes de los tests y las borra al final."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_funeraria.db"):
        os.remove("test_funeraria.db")


@pytest.fixture(scope="module")
def client():
    """
    TestClient sin context manager → no ejecuta el lifespan,
    evitando la conexión a PostgreSQL.
    app.state.limiter ya está seteado a nivel de módulo en main.py.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(client):
    """Registra un admin de prueba y devuelve su token JWT."""
    db = TestingSessionLocal()
    try:
        from app.models.user import User
        from app.security import hash_password
        existing = db.query(User).filter(User.email == "testadmin@test.com").first()
        if not existing:
            admin = User(
                nombre="Test Admin",
                email="testadmin@test.com",
                telefono="8090000001",
                password=hash_password("Admin@Test1"),
                rol="admin",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

    res = client.post("/login", json={"email": "testadmin@test.com", "password": "Admin@Test1"})
    assert res.status_code == 200
    return res.json()["access_token"]
