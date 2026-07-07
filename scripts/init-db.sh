#!/usr/bin/env bash
# Apply sql/*.sql to the running container. Idempotent. Uses sqlcmd INSIDE the
# container, so no host-side sqlcmd install is required.
set -euo pipefail

cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a

CONTAINER=fabric-local-sql
SQLCMD='/opt/mssql-tools18/bin/sqlcmd'
DB_NAME="${MS_FABRIC_DB:-fabric_mock}"   # sql/*.sql reference this via $(DbName)

echo "Waiting for SQL Server to accept connections..."
for i in $(seq 1 30); do
  if docker exec "$CONTAINER" $SQLCMD -S localhost -U sa -P "$SA_PASSWORD" -C -Q "SELECT 1" -b >/dev/null 2>&1; then
    echo "  ready."
    break
  fi
  sleep 3
  [ "$i" = "30" ] && { echo "  timed out waiting for SQL Server"; exit 1; }
done

for f in sql/01_init_db.sql sql/02_schema.sql sql/03_seed.sql; do
  echo "Applying $f (db=$DB_NAME) ..."
  docker exec -i "$CONTAINER" $SQLCMD -S localhost -U sa -P "$SA_PASSWORD" -C -b -v DbName="$DB_NAME" < "$f"
done

echo "Seed complete."
