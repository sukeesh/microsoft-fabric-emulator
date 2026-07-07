"""Smoke + correctness tests against the LOCAL mock. Requires `make up && make seed`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from fabric_connector import FabricConnector  # noqa: E402
from fabric_connector import queries  # noqa: E402


@pytest.fixture(scope="module")
def fab():
    with FabricConnector() as f:
        yield f


def test_ping(fab):
    assert fab.ping() is True


def test_seed_row_counts(fab):
    assert fab.query("SELECT COUNT(*) AS n FROM dbo.fact_sales")[0]["n"] == 6
    assert fab.query("SELECT COUNT(*) AS n FROM dbo.dim_product")[0]["n"] == 3


def test_total_revenue(fab):
    total = fab.query("SELECT SUM(total_amount) AS t FROM dbo.fact_sales")[0]["t"]
    assert float(total) == 3305.00  # 600+155+500+240+310+1500


def test_sales_by_product_top(fab):
    rows = fab.query(queries.SALES_BY_PRODUCT)
    # Support Plan: 500 + 1500 = 2000 is the top revenue line.
    assert rows[0]["product_name"] == "Support Plan"
    assert float(rows[0]["revenue"]) == 2000.00
