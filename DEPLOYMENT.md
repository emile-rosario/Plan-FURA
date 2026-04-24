# 🚀 Guía de Deployment

Este proyecto está configurado para deployarse en **Netlify** (frontend) y **Railway** (backend).

## 1️⃣ Netlify (Frontend)

1. Ve a https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Selecciona **GitHub**
4. Autoriza Netlify y selecciona el repo `Plan-FURA`
5. Configuración automática:
   - **Build command**: (dejalo vacío, solo HTML)
   - **Publish directory**: `frontend`
6. Click **Deploy site**
7. Espera ~2 min. Tu sitio estará en `https://[nombre-random].netlify.app`

## 2️⃣ Railway (Backend + Base de datos)

1. Ve a https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Autoriza Railway y selecciona `Plan-FURA`
4. Railway creará automáticamente:
   - Servicio Python (backend)
   - PostgreSQL (base de datos)

### Configurar variables de entorno en Railway:

En el panel de Railway, abre la sección **"Variables"** para el servicio Python y agrega:

```
SECRET_KEY=generador_seguro_aqui_32_caracteres_hex
ADMIN_PASSWORD=CambiaEstaClave@2025!
DB_HOST={DB_HOST de PostgreSQL}
DB_PORT={DB_PORT de PostgreSQL}
DB_NAME=funeraria_rancier
DB_USER={DB_USER de PostgreSQL}
DB_PASSWORD={DB_PASSWORD de PostgreSQL}
ALLOWED_HOSTS=localhost,127.0.0.1,[tu-dominio-railway].railway.app
CORS_ORIGINS=http://localhost:5500,https://[tu-netlify].netlify.app,[tu-dominio-railway].railway.app
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM=noreply@funerariarancier.com
FRONTEND_URL=https://[tu-netlify].netlify.app
APP_ENV=production
```

⚠️ **Importante**: Railway genera automáticamente `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`. Cópialos del tab de PostgreSQL.

5. Click **Deploy**
6. Espera ~5 min. Tu API estará en `https://[tu-backend].railway.app`

## 3️⃣ Conectar Frontend con Backend

Una vez tengas las URLs:

1. Abre el código del frontend (ej: `frontend/catalogo.html`)
2. Busca referencias a `http://localhost:8000` o la URL del backend
3. Reemplaza con `https://[tu-backend].railway.app`
4. Commit y push a GitHub
5. Netlify redeploy automáticamente

## 📋 Checklist Final

- [ ] Frontend deployado en Netlify
- [ ] Backend deployado en Railway
- [ ] Base de datos PostgreSQL creada
- [ ] Variables de entorno configuradas
- [ ] Frontend apuntando a URL correcta del backend
- [ ] CORS configurado correctamente
- [ ] Prueba login en https://[tu-netlify].netlify.app

## 🔗 URLs después del deployment

- **Frontend**: `https://[tu-netlify].netlify.app`
- **Backend API**: `https://[tu-backend].railway.app`
- **Docs API**: `https://[tu-backend].railway.app/docs`
