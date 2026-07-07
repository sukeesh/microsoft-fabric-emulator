"""Entra ID (Azure AD) service-principal token acquisition for real Fabric.

Fabric's SQL endpoint does not accept SQL logins — only Entra ID. We exchange
client_id/tenant_id/client_secret for an access token scoped to the Azure SQL
resource, then hand it to pyodbc via the SQL_COPT_SS_ACCESS_TOKEN attribute.
"""
from __future__ import annotations

import struct

from .config import FabricConfig

# pyodbc pre-connect attribute for an Entra access token.
SQL_COPT_SS_ACCESS_TOKEN = 1256
# Token audience for Azure SQL / Fabric Warehouse.
_SQL_SCOPE = "https://database.windows.net/.default"


def access_token_struct(cfg: FabricConfig) -> bytes:
    """Return the packed access-token struct pyodbc expects in attrs_before."""
    missing = [
        name
        for name, val in (
            ("MS_FABRIC_CLIENT_ID", cfg.client_id),
            ("MS_FABRIC_TENANT_ID", cfg.tenant_id),
            ("MS_FABRIC_CLIENT_SECRET", cfg.client_secret),
        )
        if not val
    ]
    if missing:
        raise RuntimeError(
            "Fabric (non-local) target requires service-principal creds; missing: "
            + ", ".join(missing)
        )

    # Imported lazily so local-only use doesn't need azure-identity installed.
    from azure.identity import ClientSecretCredential

    credential = ClientSecretCredential(
        tenant_id=cfg.tenant_id,
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
    )
    token = credential.get_token(_SQL_SCOPE).token
    token_bytes = token.encode("utf-16-le")
    return struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
