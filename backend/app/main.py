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
                    nombre="Plan Digno",
                    descripcion="Servicio funerario completo en casa o funeraria. Cobertura 3 meses menores 60, 6 meses mayores. Desembolso RD$.",
                    precio_mensual=Decimal("350.00"),
                    beneficios=[
                        "Ambulancia D.N. y prov. Sto. Dgo.",
                        "Botellones de agua",
                        "Ataúd Digno",
                        "Autobus para acompañantes",
                        "Carroza funebre"
                    ],
                    activo=True, destacado=False,
                ),
                Plan(
                    nombre="Plan Pomposo",
                    descripcion="Servicio funerario completo en casa o funeraria. Cobertura 3 meses menores 60, 6 meses mayores. Desembolso RD$10,000.",
                    precio_mensual=Decimal("500.00"),
                    beneficios=[
                        "Ambulancia D.N. y prov. Sto. Dgo.",
                        "Botellones de agua",
                        "Ataúd Pomposo",
                        "Capilla velatoria",
                        "Autobus para acompañantes"
                    ],
                    activo=True, destacado=False,
                ),
                Plan(
                    nombre="Plan Majestuoso",
                    descripcion="Servicio funerario completo en casa o funeraria. Cobertura 3 meses menores 60, 6 meses mayores. Desembolso RD$15,000.",
                    precio_mensual=Decimal("750.00"),
                    beneficios=[
                        "Ambulancia D.N. y prov. Sto. Dgo.",
                        "Botellones de agua",
                        "Ataúd Majestuoso",
                        "Capilla velatoria",
                        "Autobus para acompañantes"
                    ],
                    activo=True, destacado=False,
                ),
                Plan(
                    nombre="Plan Deluxe",
                    descripcion="Servicio funerario completo en casa o funeraria. El plan mas completo. Cobertura 3 meses menores 60, 6 meses mayores. Desembolso RD$20,000.",
                    precio_mensual=Decimal("900.00"),
                    beneficios=[
                        "Ambulancia D.N. y prov. Sto. Dgo.",
                        "Botellones de agua",
                        "Ataúd Deluxe"
                    ],
                    activo=True, destacado=True,
                ),
            ]
            db.add_all(planes)
            logger.info("Planes de ejemplo insertados.")

        _desc = (
            "Fabricado en metal de alta resistencia, diseñado para brindar una presentación "
            "sobria y elegante. Terminación con pintura electrostática, que ofrece mayor "
            "durabilidad, excelente acabado y protección contra el desgaste. Ideal para quienes "
            "buscan calidad, seguridad y una opción digna para despedir a su ser querido."
        )
        _modelos = [
            ("Ataúd Digno",        "assets/img/catalogo/ataud-digno.jpeg",    "assets/img/catalogo/ataud-digno-2.jpeg",    Decimal("25000.00"), False),
            ("Ataúd Pomposo",      "assets/img/catalogo/ataud-pomposo.jpeg",  "assets/img/catalogo/ataud-pomposo-2.jpeg",  Decimal("35000.00"), False),
            ("Ataúd Deluxe",       "assets/img/catalogo/deluxe.jpeg",         "assets/img/catalogo/deluxe-2.jpeg",         Decimal("45000.00"), False),
            ("Ataúd Deluxe Pro",   "assets/img/catalogo/deluxe-pro.jpeg",     "assets/img/catalogo/deluxe-pro-2.jpeg",     Decimal("60000.00"), True),
            ("Ataúd Majestuoso Pro","assets/img/catalogo/majestuoso-pro.jpeg","assets/img/catalogo/majestuoso-pro-2.jpeg", Decimal("75000.00"), True),
        ]

        # Borra registros que no sean los 5 modelos reales
        nombres_validos = [m[0] for m in _modelos]
        db.query(Coffin).filter(~Coffin.nombre.in_(nombres_validos)).delete(synchronize_session=False)

        for nombre, img, img2, precio, destacado in _modelos:
            existing = db.query(Coffin).filter(Coffin.nombre == nombre).first()
            if existing:
                existing.imagen_url   = img
                existing.imagen_url_2 = img2
                existing.material     = "Metal"
                existing.descripcion  = _desc
                existing.disponible   = True
                existing.destacado    = destacado
            else:
                db.add(Coffin(
                    nombre=nombre, material="Metal", descripcion=_desc,
                    precio=precio, disponible=True, destacado=destacado,
                    imagen_url=img, imagen_url_2=img2,
                ))
        logger.info("Ataúdes sincronizados.")

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
