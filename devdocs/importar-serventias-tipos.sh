#!/usr/bin/env bash
set -euo pipefail

APP_CONTAINER=${APP_CONTAINER:-despesa_app}
DB_CONTAINER=${DB_CONTAINER:-despesa_db}
DB_USER=${DB_USER:-admin}
DB_NAME=${DB_NAME:-despesas_db}
BASE_URL=${BASE_URL:-http://localhost:8080}
API_USER=${API_USER:-cogex_admin}
API_PASS=${API_PASS:-password}
SERVENTIAS_FILE=${SERVENTIAS_FILE:-/home/fernando/codes/docs-exofi-26/Serventias.txt}
TIPOS_FILE=${TIPOS_FILE:-/home/fernando/codes/docs-exofi-26/Tipos_de_Cartorio.txt}

if [[ ! -f "$SERVENTIAS_FILE" ]]; then
  echo "Arquivo de serventias não encontrado: $SERVENTIAS_FILE" >&2
  exit 1
fi

if [[ ! -f "$TIPOS_FILE" ]]; then
  echo "Arquivo de tipos de cartorio não encontrado: $TIPOS_FILE" >&2
  exit 1
fi

echo "Copiando arquivos para o container $APP_CONTAINER..."
docker cp "$SERVENTIAS_FILE" "$APP_CONTAINER":/Serventias.txt

docker cp "$TIPOS_FILE" "$APP_CONTAINER":/Tipos_de_Cartorio.txt

echo "Resetando schema public em $DB_CONTAINER..."
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Reiniciando $APP_CONTAINER para recriar o schema..."
docker restart "$APP_CONTAINER" >/dev/null

echo "Aguardando API ficar pronta..."
ready=0
for i in {1..30}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -u "$API_USER:$API_PASS" "$BASE_URL/hello" || true)
  if [[ "$status" == "200" ]]; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" != "1" ]]; then
  echo "API não ficou pronta a tempo (status=$status)" >&2
  exit 1
fi

echo "Importando serventias..."
resp=$(curl -sS -u "$API_USER:$API_PASS" -w "\nHTTP %{http_code}\n" -X POST "$BASE_URL/api/serventias/import-file?path=/Serventias.txt")
echo "$resp" | head -c 400
printf "\n"

echo "Importando tipos de cartorio..."
resp=$(curl -sS -u "$API_USER:$API_PASS" -w "\nHTTP %{http_code}\n" -X POST "$BASE_URL/api/tipos-cartorio/import-file?path=/Tipos_de_Cartorio.txt")
echo "$resp" | head -c 400
printf "\n"

echo "Concluído."
