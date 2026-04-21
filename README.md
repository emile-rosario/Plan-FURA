# Funerarias Rancier — Plataforma Web

Un sistema web completo que construí para digitalizar y modernizar la gestión de una funeraria real en República Dominicana. Desde la presentación de servicios al cliente hasta un panel de administración funcional.

---

## ¿Qué es esto?

Este proyecto nació de la necesidad de llevar una funeraria tradicional al mundo digital. No solo es una página web de presentación — tiene un backend real, autenticación de usuarios, catálogo de productos, planes de suscripción y formulario de contacto, todo conectado.

Lo construí de cero usando **FastAPI** en el backend y **HTML/CSS/JS** en el frontend, con **PostgreSQL** como base de datos.

---

## Lo que puedes hacer en la plataforma

**Como visitante:**
- Ver los planes funerarios disponibles con precios y comparativas
- Explorar el catálogo de ataúdes con fotos y filtros
- Enviar un mensaje de contacto directamente desde la web

**Como cliente registrado:**
- Crear una cuenta y gestionar tu perfil
- Contratar un plan funerario
- Ver el estado de tu suscripción desde tu panel personal

**Como administrador:**
- Gestionar planes y ataúdes (crear, editar, eliminar)
- Ver todos los mensajes de contacto recibidos
- Subir imágenes al catálogo

---

## Tecnologías que usé

| Parte | Tecnología |
|-------|-----------|
| Backend | FastAPI + Python |
| Base de datos | PostgreSQL |
| Autenticación | JWT + bcrypt |
| Frontend | HTML, CSS, JavaScript vanilla |
| ORM | SQLAlchemy |

---

## Páginas del frontend

- **`index.html`** — Página principal con presentación y servicios
- **`planes-funerarios.html`** — Planes con tabla comparativa y preguntas frecuentes
- **`catalogo.html`** — Catálogo de ataúdes estilo e-commerce con filtros
- **`login.html`** — Inicio de sesión y registro
- **`dashboard.html`** — Panel del cliente
- **`contacto.html`** — Formulario de contacto

---

## Cómo correrlo localmente

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Configura tu .env con los datos de tu PostgreSQL
uvicorn app.main:app --reload --port 8000
```

### Frontend

Abre `frontend/index.html` con **Live Server** desde VS Code, o usa:

```bash
cd frontend
python -m http.server 5500
```

Al iniciar por primera vez el backend, se crean automáticamente datos de prueba y un usuario admin con las credenciales que están en el archivo `backend/.env` (o `.env.example` como referencia).

---

## Estado del proyecto

Actualmente en desarrollo activo. Próximo paso: integración con **Azul** (pasarela de pagos dominicana) para procesar suscripciones en línea.

---

*Desarrollado por Emile Rosario — República Dominicana 🇩🇴*
