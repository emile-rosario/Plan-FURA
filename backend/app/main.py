"""
Backend Funeraria Rancier — Punto de entrada principal.
FastAPI + PostgreSQL + JWT + bcrypt + slowapi
"""
import logging
import os
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base, SessionLocal, check_db_connection
from app.limiter import limiter
from app.routers import auth, coffins, plans, uploads, contacto, suscripciones, password_reset

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza de la aplicación."""
    logger.info("Iniciando Funeraria Rancier Backend...")

    if not check_db_connection():
        logger.error("❌ No se pudo conectar a PostgreSQL. Verifica la configuración.")
    else:
        logger.info("✅ Conexión a PostgreSQL establecida.")

    Base.metadata.create_all(bind=engine)
    seed_data()

    os.makedirs("uploads", exist_ok=True)

    logger.info("✅ Backend iniciado correctamente en modo: %s", settings.APP_ENV)
    yield
    logger.info("Backend detenido.")


# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Funeraria Rancier — API",
    description="API REST para gestión de servicios funerarios, planes y ataúdes.",
    version="3.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
)


# ── Rate Limiter ───────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Middlewares ────────────────────────────────────────────────
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Manejador global de errores ────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Error no manejado en %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Contacta al administrador."},
    )


# ── Static files ───────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── Routers ────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(coffins.router)
app.include_router(plans.router)
app.include_router(uploads.router)
app.include_router(contacto.router)
app.include_router(suscripciones.router)
app.include_router(password_reset.router)


# ── Health Check ───────────────────────────────────────────────
@app.get("/", tags=["Sistema"])
def root():
    return {
        "app": "Funeraria Rancier API",
        "version": "3.1.0",
        "status": "activo",
        "db": "postgresql",
    }


@app.get("/health", tags=["Sistema"])
def health():
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }


# ── Seed Data ──────────────────────────────────────────────────
def seed_data():
    """Insertar datos de ejemplo si las tablas están vacías."""
    from app.models.funeral import Plan, Coffin
    from app.security import hash_password
    from app.models.user import User

    db = SessionLocal()
    try:
        if db.query(Plan).count() == 0:
            planes = [
                Plan(
                    nombre="Plan Esencial",
                    descripcion="Servicio completo de velación, traslado y trámites legales básicos.",
                    precio_mensual=Decimal("850.00"),
                    beneficios=[
                        "Velación 24 horas", "Traslado local", "Trámites legales",
                        "Urna básica", "Servicio de capilla"
                    ],
                    activo=True, destacado=False,
                ),
                Plan(
                    nombre="Plan Familiar",
                    descripcion="Cobertura para 4 miembros del núcleo familiar, sala VIP y flores.",
                    precio_mensual=Decimal("1500.00"),
                    beneficios=[
                        "Todo del Plan Esencial", "Cobertura familiar (4 personas)",
                        "Sala VIP", "Arreglo floral incluido", "Libro de condolencias"
                    ],
                    activo=True, destacado=True,
                ),
                Plan(
                    nombre="Plan Premium",
                    descripcion="Cobertura completa con transmisión en vivo y acompañamiento 24/7.",
                    precio_mensual=Decimal("2800.00"),
                    beneficios=[
                        "Cobertura familiar ilimitada", "Sala de honor",
                        "Transmisión en vivo", "Libro digital de condolencias",
                        "Acompañamiento 24/7", "Transporte internacional"
                    ],
                    activo=True, destacado=False,
                ),
                Plan(
                    nombre="Plan Previsión",
                    descripcion="Ahorro anticipado. Congela el precio actual del servicio.",
                    precio_mensual=Decimal("600.00"),
                    beneficios=[
                        "Precio congelado", "Sin cuota de inscripción",
                        "Transferible", "Cobertura inmediata"
                    ],
                    activo=True, destacado=False,
                ),
            ]
            db.add_all(planes)
            logger.info("Planes de ejemplo insertados.")

        if db.query(Coffin).count() == 0:
            _desc = (
                "Fabricado en metal de alta resistencia, diseñado para brindar una presentación "
                "sobria y elegante. Terminación con pintura electrostática, que ofrece mayor "
                "durabilidad, excelente acabado y protección contra el desgaste. Ideal para quienes "
                "buscan calidad, seguridad y una opción digna para despedir a su ser querido."
            )
            ataudes = [
                Coffin(
                    nombre="Ataúd Digno", material="Metal",
                    descripcion=_desc,
                    precio=Decimal("25000.00"), disponible=True,
                    imagen_url="assets/img/catalogo/ataud-digno.jpeg",
                ),
                Coffin(
                    nombre="Ataúd Pomposo", material="Metal",
                    descripcion=_desc,
                    precio=Decimal("35000.00"), disponible=True,
                    imagen_url="assets/img/catalogo/ataud-pomposo.jpeg",
                ),
                Coffin(
                    nombre="Ataúd Deluxe", material="Metal",
                    descripcion=_desc,
                    precio=Decimal("45000.00"), disponible=True,
                    imagen_url="assets/img/catalogo/deluxe.jpeg",
                ),
                Coffin(
                    nombre="Ataúd Deluxe Pro", material="Metal",
                    descripcion=_desc,
                    precio=Decimal("60000.00"), disponible=True, destacado=True,
                    imagen_url="assets/img/catalogo/deluxe-pro.jpeg",
                ),
                Coffin(
                    nombre="Ataúd Majestuoso Pro", material="Metal",
                    descripcion=_desc,
                    precio=Decimal("75000.00"), disponible=True, destacado=True,
                    imagen_url="assets/img/catalogo/majestuoso-pro.jpeg",
                ),
            ]
            db.add_all(ataudes)
            logger.info("Ataúdes insertados.")

        if db.query(User).filter(User.rol == "admin").count() == 0:
            admin = User(
                nombre="Administrador Rancier",
                email="admin@funerariarancier.com",
                telefono="8095551234",
                password=hash_password(settings.ADMIN_PASSWORD),
                rol="admin",
            )
            db.add(admin)
            logger.info("Usuario admin creado: admin@funerariarancier.com")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Error en seed_data: %s", e)
    finally:
        db.close()
