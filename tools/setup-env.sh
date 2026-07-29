#!/usr/bin/env bash
# Erzeugt .env mit projekt-eindeutigen Ports und Namen (Kollisionsschutz).
# Ableitung aus dem absoluten Projektpfad via cksum, damit jeder Klon in einem
# anderen Ordner automatisch andere Ports und Container-Namen bekommt.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  echo ".env existiert bereits - wird nicht ueberschrieben. Zum Neu-Erzeugen zuerst loeschen."
  exit 0
fi

name_taken() {
  docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx "$1" && return 0
  docker volume ls --format '{{.Name}}' 2>/dev/null | grep -qx "$1" && return 0
  docker network ls --format '{{.Name}}' 2>/dev/null | grep -qx "$1" && return 0
  return 1
}
port_in_use() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1 && return 0
  docker ps --format '{{.Ports}}' 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}
free_port() {
  local p="$1"; while port_in_use "$p"; do p=$((p+1)); done; echo "$p"
}

HASH="$(printf '%s' "$ROOT_DIR" | cksum | awk '{print $1}')"
POSTFIX="$(printf '%s' "$HASH" | tail -c 6)"
OFFSET=$(( HASH % 50 ))

PROJECT="wetterwarte-$POSTFIX"
while name_taken "$PROJECT"; do POSTFIX="${POSTFIX}x"; PROJECT="wetterwarte-$POSTFIX"; done

BACKEND_PORT="$(free_port $(( 6150 + OFFSET )))"
FRONTEND_PORT="$(free_port $(( 6151 + OFFSET )))"
DB_PORT="$(free_port $(( 6152 + OFFSET )))"
REDIS_PORT="$(free_port $(( 6153 + OFFSET )))"

DB_PASS="$(openssl rand -hex 24)"
SECRET="$(openssl rand -hex 32)"

umask 077
cat > "$ENV_FILE" <<EOF
# Automatisch erzeugt von tools/setup-env.sh - projekt-eindeutig, NICHT einchecken.
COMPOSE_PROJECT_NAME=$PROJECT

BACKEND_PORT=$BACKEND_PORT
FRONTEND_PORT=$FRONTEND_PORT
DB_PORT=$DB_PORT
REDIS_PORT=$REDIS_PORT

POSTGRES_USER=wetterwarte
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_DB=wetterwarte
DATABASE_URL=postgresql+asyncpg://wetterwarte:$DB_PASS@localhost:$DB_PORT/wetterwarte

REDIS_URL=redis://localhost:$REDIS_PORT/0

APP_SECRET=$SECRET
EOF

echo "Projekt:   $PROJECT"
echo "Backend:   $BACKEND_PORT"
echo "Frontend:  $FRONTEND_PORT"
echo "Postgres:  $DB_PORT"
echo "Redis:     $REDIS_PORT"
echo ".env geschrieben nach $ENV_FILE"
