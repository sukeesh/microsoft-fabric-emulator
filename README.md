# fabric-local — local Microsoft Fabric SQL connector + mock

Your Fabric trial expired, but Fabric's Warehouse / SQL endpoint speaks **TDS +
T-SQL**, i.e. it's wire-compatible with SQL Server. So this repo runs a **real
local SQL Server** as a faithful stand-in, seeds it with a Fabric-shaped star
schema, and ships a Python connector whose auth is **auto-selected by host**:

| `MS_FABRIC_SQL_CONNECTION_STRING` host | Auth used                              |
|----------------------------------------|----------------------------------------|
| `localhost` / `127.0.0.1`              | SQL auth against the docker mock (`sa`) |
| `*.datawarehouse.fabric.microsoft.com` | Entra ID service-principal token       |

**The same application code runs against both.** To go from local to cloud you
only change `MS_FABRIC_SQL_CONNECTION_STRING` (and fill in the SP creds) — no
code change.

## Prerequisites (already satisfied on this machine)
- Docker Desktop (with Rosetta, for the amd64 SQL Server image on Apple Silicon)
- `ODBC Driver 18 for SQL Server` (installed). If missing: `brew install msodbcsql18`

## Quickstart (local mock)
```bash
cp .env.example .env        # defaults already target localhost
make up                     # start SQL Server 2022 (first pull/boot is slow on ARM)
make seed                   # create the DB (name from MS_FABRIC_DB) + schema + sample data
make demo                   # connector connects & prints sample analytics
make test                   # pytest asserts seeded aggregates
```

## Using the connector in your own code
```python
from fabric_connector import FabricConnector

with FabricConnector() as fab:          # reads MS_FABRIC_* from env / .env
    rows = fab.query("SELECT * FROM dbo.fact_sales WHERE quantity > ?", [5])
    print(rows)
```

## Switching to real Fabric later
In `.env`:
```
MS_FABRIC_SQL_CONNECTION_STRING=<your-workspace>.datawarehouse.fabric.microsoft.com:1433
MS_FABRIC_DB=<your-warehouse-name>
MS_FABRIC_CLIENT_ID=...
MS_FABRIC_TENANT_ID=...
MS_FABRIC_CLIENT_SECRET=...
```
The connector detects the non-local host, fetches an Entra token for the service
principal (scope `https://database.windows.net/.default`), and passes it to
pyodbc via `SQL_COPT_SS_ACCESS_TOKEN`. Nothing else changes.

> ⚠️ **Rotate any client secret that has been shared in plaintext** (chat, tickets, etc.).

## Layout
- `docker-compose.yml` — SQL Server 2022 mock (amd64 emulation, healthcheck, volume)
- `sql/` — `01_init_db` / `02_schema` / `03_seed` (all idempotent)
- `scripts/init-db.sh` — waits for readiness then applies the SQL (uses in-container sqlcmd)
- `connector/fabric_connector/` — `config.py` (env → conn string), `auth.py` (SP token),
  `client.py` (`FabricConnector`), `queries.py` (sample analytics)

## Notes / caveats
- **ARM emulation**: the official SQL Server image is x86-only; it runs under Rosetta.
  If it's flaky, swap the image for `mcr.microsoft.com/azure-sql-edge` (ARM-native,
  T-SQL subset) in `docker-compose.yml`.
- **T-SQL fidelity**: local SQL Server runs the full T-SQL surface. A handful of
  Fabric-specific niceties (e.g. `COPY INTO` from OneLake, cross-warehouse queries)
  have no local equivalent; standard analytic SQL behaves identically.
