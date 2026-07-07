#!/usr/bin/env bash
#
#   ./fabric-local.sh run     # start the local Fabric (SQL Server mock) + seed
#   ./fabric-local.sh stop    # stop it
#
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

[ -f .env ] && { set -a; . ./.env; set +a; }
SA_PASSWORD="${SA_PASSWORD:-LocalFabric_123!}"
MS_FABRIC_DB="${MS_FABRIC_DB:-fabric_mock}"
CONTAINER=fabric-local-sql
SQLCMD='/opt/mssql-tools18/bin/sqlcmd'

case "${1:-run}" in
  stop)
    docker compose down
    exit 0
    ;;
  run|"")
    echo "[fabric-local] starting SQL Server mock…"
    docker compose up -d >/dev/null

    echo "[fabric-local] waiting until healthy…"
    for i in $(seq 1 40); do
      [ "$(docker inspect --format '{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo x)" = "healthy" ] && break
      [ "$i" = "40" ] && { echo "[fabric-local] ERROR: not healthy"; docker compose logs --tail 20; exit 1; }
      sleep 3
    done

    tbls="$(docker exec "$CONTAINER" $SQLCMD -S localhost -U sa -P "$SA_PASSWORD" -C -h -1 \
            -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM [$MS_FABRIC_DB].sys.tables" 2>/dev/null | tr -d '[:space:]' || true)"
    if ! [[ "$tbls" =~ ^[0-9]+$ ]] || [ "$tbls" -eq 0 ]; then
      echo "[fabric-local] seeding…"
      ./scripts/init-db.sh >/dev/null
    fi

    echo "[fabric-local] READY on localhost:1433 (db: $MS_FABRIC_DB). Point your Fabric connector here."
    echo
    docker compose ps
    echo
    echo "[fabric-local] streaming logs — Ctrl+C to detach (mock keeps running; './fabric-local.sh stop' to stop)."
    echo
    exec docker compose logs -f
    ;;
  *)
    echo "usage: ./fabric-local.sh [run|stop]"; exit 1
    ;;
esac
