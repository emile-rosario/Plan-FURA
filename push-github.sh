#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  push-github.sh  —  Sube el proyecto a GitHub automáticamente
#  Repositorio: https://github.com/emile-rosario/Plan-FURA
# ─────────────────────────────────────────────────────────────

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_URL="https://github.com/emile-rosario/Plan-FURA.git"
BRANCH="main"

echo ""
echo "🚀 Iniciando push a GitHub..."
echo "📁 Carpeta: $REPO_DIR"
echo ""

cd "$REPO_DIR"

# Limpiar .git roto si existe pero no funciona
if [ -d ".git" ]; then
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "🧹 Limpiando repositorio git corrupto..."
    rm -rf .git
  fi
fi

# Inicializar git fresco si no existe
if [ ! -d ".git" ]; then
  echo "⚙️  Inicializando repositorio git..."
  git init -b "$BRANCH"
else
  echo "✅ Repositorio git encontrado."
fi

# Configurar remote
if ! git remote get-url origin > /dev/null 2>&1; then
  git remote add origin "$REMOTE_URL"
else
  git remote set-url origin "$REMOTE_URL"
fi

# Configurar usuario
git config user.email "emilerosario4@gmail.com"
git config user.name "Emile Rosario"

# Agregar todos los archivos
echo ""
echo "📦 Agregando archivos..."
git add --all

echo ""
echo "📝 Cambios a subir:"
git status --short

echo ""
echo "💾 Haciendo commit..."
git commit -m "fix(backend): correcciones de seguridad y bugs

- Eliminar contraseña admin del log en seed_data
- Eliminar 'null' de CORS_ORIGINS (riesgo de seguridad)
- Corregir response_model list[dict] en /contacto por schema tipado
- Agregar ContactoDetailResponse schema para endpoint admin
- Corregir eager-load faltante en contratar_plan (plan siempre null)
- Cambiar comparaciones == True a .is_(True) en filtros SQLAlchemy
- Eliminar import 'event' no utilizado en database.py
- Agregar .gitignore para backend Python" 2>/dev/null || echo "ℹ️  Sin cambios nuevos que commitear."

echo ""
echo "🔑 Cuando pida 'Username': escribe   emile-rosario"
echo "   Cuando pida 'Password': pega tu   GitHub Token"
echo ""

git push -u origin "$BRANCH" --force

echo ""
echo "✅ ¡Listo! Cambios subidos a:"
echo "   https://github.com/emile-rosario/Plan-FURA"
echo ""
