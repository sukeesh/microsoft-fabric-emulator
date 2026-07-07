"""Connection configuration driven entirely by MS_FABRIC_* env vars.

The single switch is the HOST in MS_FABRIC_SQL_CONNECTION_STRING:

    localhost:1433   -> LOCAL profile  -> SQL auth against the docker mock (sa)
    *.fabric...:1433 -> FABRIC profile -> Entra ID service-principal token auth

Nothing else changes between local and cloud, so the same application code runs
against both.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # loads .env from cwd / project root if present

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
ODBC_DRIVER = "ODBC Driver 18 for SQL Server"


@dataclass
class FabricConfig:
    host: str
    port: int
    database: str
    is_local: bool
    # local (SQL auth)
    sa_password: str | None = None
    # fabric (service principal)
    client_id: str | None = None
    tenant_id: str | None = None
    client_secret: str | None = None

    @classmethod
    def from_env(cls) -> "FabricConfig":
        conn = os.environ.get("MS_FABRIC_SQL_CONNECTION_STRING", "localhost:1433").strip()
        host, _, port_s = conn.partition(":")
        host = host.strip()
        port = int(port_s) if port_s else 1433

        database = os.environ.get("MS_FABRIC_DB", "fabric_mock").strip().strip("'\"")
        is_local = host.lower() in _LOCAL_HOSTS

        return cls(
            host=host,
            port=port,
            database=database,
            is_local=is_local,
            sa_password=os.environ.get("SA_PASSWORD"),
            client_id=os.environ.get("MS_FABRIC_CLIENT_ID"),
            tenant_id=os.environ.get("MS_FABRIC_TENANT_ID"),
            client_secret=os.environ.get("MS_FABRIC_CLIENT_SECRET"),
        )

    @property
    def profile(self) -> str:
        return "local" if self.is_local else "fabric"

    def odbc_connection_string(self) -> str:
        """Base ODBC string. Auth differs by profile (see client.connect)."""
        parts = [
            f"DRIVER={{{ODBC_DRIVER}}}",
            f"SERVER={self.host},{self.port}",
            f"DATABASE={self.database}",
            "Encrypt=yes",
        ]
        if self.is_local:
            # Self-signed dev cert on the local container.
            parts.append("TrustServerCertificate=yes")
            parts.append("UID=sa")
            parts.append(f"PWD={self.sa_password}")
        else:
            # Real Fabric presents a valid public cert; token supplied separately.
            parts.append("TrustServerCertificate=no")
        return ";".join(parts) + ";"
