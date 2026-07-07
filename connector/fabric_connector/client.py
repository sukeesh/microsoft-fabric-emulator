"""FabricConnector — one stable API for both the local mock and real Fabric.

    from fabric_connector import FabricConnector

    with FabricConnector() as fab:
        rows = fab.query("SELECT TOP 5 * FROM dbo.fact_sales")
"""
from __future__ import annotations

from typing import Any, Sequence

import pyodbc

from .auth import SQL_COPT_SS_ACCESS_TOKEN, access_token_struct
from .config import FabricConfig


class FabricConnector:
    def __init__(self, config: FabricConfig | None = None):
        self.config = config or FabricConfig.from_env()
        self._conn: pyodbc.Connection | None = None

    # -- lifecycle ---------------------------------------------------------
    def connect(self) -> "FabricConnector":
        conn_str = self.config.odbc_connection_string()
        if self.config.is_local:
            self._conn = pyodbc.connect(conn_str, autocommit=True)
        else:
            token_struct = access_token_struct(self.config)
            self._conn = pyodbc.connect(
                conn_str,
                autocommit=True,
                attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct},
            )
        return self

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "FabricConnector":
        return self.connect()

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- queries -----------------------------------------------------------
    def query(self, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
        """Run a SELECT and return rows as a list of dicts."""
        cur = self._cursor().execute(sql, *(params or ()))
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return rows

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> int:
        """Run a non-SELECT statement; return affected row count."""
        cur = self._cursor().execute(sql, *(params or ()))
        n = cur.rowcount
        cur.close()
        return n

    def ping(self) -> bool:
        return self.query("SELECT 1 AS ok")[0]["ok"] == 1

    # -- internal ----------------------------------------------------------
    def _cursor(self) -> pyodbc.Cursor:
        if self._conn is None:
            raise RuntimeError("Not connected — call connect() or use a `with` block.")
        return self._conn.cursor()
