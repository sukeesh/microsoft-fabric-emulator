"""End-to-end demo. Connects using whatever MS_FABRIC_* env vars are set
(local mock by default) and runs the sample analytic queries.

    python connector/examples/demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fabric_connector import FabricConnector  # noqa: E402
from fabric_connector import queries  # noqa: E402


def _print_table(title: str, rows: list[dict]) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        print("(no rows)")
        return
    cols = list(rows[0].keys())
    print(" | ".join(cols))
    print("-" * 60)
    for r in rows:
        print(" | ".join(str(r[c]) for c in cols))


def main() -> None:
    with FabricConnector() as fab:
        print(f"Connected via '{fab.config.profile}' profile "
              f"to {fab.config.host}:{fab.config.port}/{fab.config.database}")
        assert fab.ping(), "ping failed"
        _print_table("Sales by product", fab.query(queries.SALES_BY_PRODUCT))
        _print_table("Sales by segment", fab.query(queries.SALES_BY_CUSTOMER_SEGMENT))
        _print_table("Monthly revenue", fab.query(queries.MONTHLY_REVENUE))


if __name__ == "__main__":
    main()
