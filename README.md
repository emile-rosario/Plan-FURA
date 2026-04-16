# 🌑 Funerarias Rancier — Web Profesional v3.0

Sistema web completo para funeraria con FastAPI, PostgreSQL y frontend moderno.

---

## 📋 Problemas encontrados en v2 y correcciones aplicadas

| Área | Problema Original | Solución v3 |
|------|------------------|-------------|
| **Base de datos** | SQLite (no apto para producción) | PostgreSQL con pool de conexiones optimizado |
| **Seguridad CORS** | `allow_origins=["*"]` — peligroso | Orígenes específicos desde `.env` |
| **Modelos** | `Float` para precios (impreciso) | `Numeric(12,2)` de PostgreSQL |
| **Modelos** | Sin índices, sin constraints | Índices, FKs con `ondelete`, `CheckConstraint` |
| **Auth** | `get_db()` dentro de `security.py` | Separado en `database.py` correctamente |
| **Config** | `DATABASE_URL` hardcodeado como SQLite | Variables de entorno para PostgreSQL |
| **Database.py** | `connect_args={"check_same_thread": False}` (SQLite-only) | Removido; QueuePool para PostgreSQL |
| **Main.py** | CORS `allow_credentials=False` con wildcard | Configuración correcta con credenciales |
| **Frontend** | `alert()` para errores de sesión | Redirección limpia sin alertas nativas |
| **Suscripciones** | Sin validación de suscripción duplicada | Verifica suscripción activa antes de crear |
| **Contraseñas** | Sin validación de fortaleza | Validación: letras + números requeridos |
| **Upload** | Sin validación de tipo real (solo content-type header) | Validación de extensión + content-type + tamaño |
| **Seed admin** | Sin usuario admin por defecto | Crea admin con credenciales configurables |

---

## 🏗️ Arquitectura del Proyecto

```
funeraria-pro/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración centralizada (pydantic-settings)
│   │   ├── database.py        # Conexión PostgreSQL con QueuePool
│   │   ├── security.py        # bcrypt + JWT + dependencias FastAPI
│   │   ├── main.py            # App FastAPI con lifespan
│   │   ├── models/
│   │   │   ├── user.py        # Modelo User con índices
│   │   │   └── funeral.py     # Plan, Coffin, Suscripcion, MensajeContacto
│   │   ├── schemas/
│   │   │   ├── user.py        # Schemas Pydantic validados
│   │   │   └── funeral.py     # Schemas con Decimal para precios
│   │   └── routers/
│   │       ├── auth.py        # /register, /login, /me
│   │       ├── coffins.py     # /ataudes CRUD
│   │       ├── plans.py       # /planes CRUD
│   │       ├── suscripciones.py # /suscripciones
│   │       ├── contacto.py    # /contacto
│   │       └── uploads.py     # /uploads/imagen (seguro)
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
└── frontend/
    ├── index.html             # Página principal (hero + servicios + planes)
    ├── planes-funerarios.html # Planes con tabla comparativa + FAQ
    ├── catalogo.html          # Catálogo estilo ecommerce con filtros/modal
    ├── login.html             # Login + Registro en un formulario
    ├── dashboard.html         # Panel de cliente con sidebar
    ├── contacto.html          # Formulario con validación frontend
    └── assets/
        └── js/
            └── api.js         # Cliente API centralizado + Auth + UI helpers
```

---

## ⚙️ Instalación y Configuración

### Requisitos
- Python 3.11+
- PostgreSQL 14+
- Node.js (opcional, para Live Server)

---

### 1. Configurar PostgreSQL

```bash
# Instalar PostgreSQL (Ubuntu/Debian)
sudo apt update && sudo apt install -y postgresql postgresql-contrib

# macOS con Homebrew
brew install postgresql@16 && brew services start postgresql@16

# Windows: Descargar desde https://www.postgresql.org/download/windows/

# Crear base de datos y usuario
sudo -u postgres psql << 'EOF'
CREATE DATABASE funeraria_rancier;
CREATE USER funeraria_user WITH ENCRYPTED PASSWORD 'funeraria_pass';
GRANT ALL PRIVILEGES ON DATABASE funeraria_rancier TO funeraria_user;
\c funeraria_rancier
GRANT ALL ON SCHEMA public TO funeraria_user;
EOF
```

---

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

Edita `.env` con tus valores reales:
```env
SECRET_KEY=genera_una_clave_segura_con_openssl_rand_hex_32
DB_HOST=localhost
DB_PORT=5432
DB_NAME=funeraria_rancier
DB_USER=funeraria_user
DB_PASSWORD=funeraria_pass
APP_ENV=development
```

Para generar una SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 3. Ejecutar el Backend

```bash
# Desde la carpeta backend/
uvicorn app.main:app --reload --port 8000
```

Al iniciar por primera vez, se crean automáticamente:
- Todas las tablas en PostgreSQL
- 4 planes funerarios de ejemplo
- 6 ataúdes de ejemplo
- Usuario admin: `admin@funerariarancier.com` / `Admin@2025`

Documentación de la API disponible en: `http://localhost:8000/docs`

---

### 4. Ejecutar el Frontend

```bash
# Opción A: Con VS Code Live Server (recomendado)
# Instala la extensión "Live Server" y abre index.html con ella

# Opción B: Con Python
cd frontend
python -m http.server 5500

# Opción C: Con Node.js
npx serve frontend -p 5500
```

Abrir en navegador: `http://localhost:5500`

---

### 5. Migraciones con Alembic (opcional, para producción)

```bash
cd backend

# Inicializar Alembic (ya viene configurado)
alembic init migrations

# Actualizar migrations/env.py para importar modelos:
# from app.models import *
# from app.database import Base
# target_metadata = Base.metadata

# Crear primera migración
alembic revision --autogenerate -m "initial"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history
```

---

## 🔌 API Endpoints

### Autenticación
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/register` | Crear cuenta | — |
| POST | `/login` | Iniciar sesión | — |
| GET | `/me` | Perfil propio | ✓ Bearer |

### Ataúdes
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/ataudes` | Listar ataúdes | — |
| GET | `/ataudes/{id}` | Ver ataúd | — |
| POST | `/ataudes` | Crear ataúd | ✓ Admin |
| PUT | `/ataudes/{id}` | Editar ataúd | ✓ Admin |
| DELETE | `/ataudes/{id}` | Eliminar ataúd | ✓ Admin |

### Planes
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/planes` | Listar planes | — |
| POST | `/planes` | Crear plan | ✓ Admin |
| PUT | `/planes/{id}` | Editar plan | ✓ Admin |
| DELETE | `/planes/{id}` | Eliminar plan | ✓ Admin |

### Suscripciones
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/suscripciones` | Contratar plan | ✓ Bearer |
| GET | `/suscripciones/mi-plan` | Ver mi plan | ✓ Bearer |
| DELETE | `/suscripciones/mi-plan` | Cancelar plan | ✓ Bearer |

### Contacto
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/contacto` | Enviar mensaje | — |
| GET | `/contacto` | Ver mensajes | ✓ Admin |

---

## 💳 Integración con Azul (República Dominicana)

El sistema está preparado para integrar Azul. Pasos:

1. Obtener credenciales en [azul.com.do](https://azul.com.do)
2. Agregar a `.env`:
```env
AZUL_MERCHANT_ID=tu_merchant_id
AZUL_AUTH1=tu_auth1
AZUL_AUTH2=tu_auth2
AZUL_ENV=sandbox   # o production
```

3. Crear router `/backend/app/routers/pagos.py`:
```python
# Endpoint de procesamiento de pago
@router.post("/pagos/procesar")
async def procesar_pago(data: PagoCreate, user=Depends(get_current_user)):
    # Llamar API de Azul con HMAC-SHA512
    # Guardar transacción en DB
    # Activar suscripción si exitoso
    ...
```

El archivo `checkout-pagos.html` ya existe como base del formulario de pago.

---

## 🔒 Seguridad implementada

- **Contraseñas**: bcrypt con costo 12 (lento por diseño)
- **JWT**: HS256 con expiración configurable
- **CORS**: Orígenes específicos, no wildcard
- **SQL Injection**: Prevenido por SQLAlchemy ORM (queries parametrizadas)
- **XSS**: `textContent` en lugar de `innerHTML` donde se renderizan datos del API
- **Uploads**: Validación de content-type + extensión + tamaño máximo + nombre UUID
- **Rate limiting**: Pendiente (recomendado: `slowapi` en producción)
- **HTTPS**: Configurar con Nginx + Let's Encrypt en producción

---

## 🚀 Despliegue en Producción

```bash
# 1. Usar variables de entorno reales
APP_ENV=production
SECRET_KEY=clave_muy_larga_y_segura_de_64_chars

# 2. Iniciar con Gunicorn + Uvicorn workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 3. Configurar Nginx como reverse proxy
# 4. Habilitar HTTPS con Let's Encrypt (certbot)
# 5. Configurar firewall (ufw)
```

---

## 👤 Credenciales de prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@funerariarancier.com | Admin@2025 |

> ⚠️ Cambiar inmediatamente en producción.
