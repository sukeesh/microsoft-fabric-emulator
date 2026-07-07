"""A few analytic queries over the star schema, to exercise the connector."""

SALES_BY_PRODUCT = """
SELECT p.product_name, p.category,
       SUM(f.quantity)      AS units,
       SUM(f.total_amount)  AS revenue
FROM dbo.fact_sales f
JOIN dbo.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_name, p.category
ORDER BY revenue DESC;
"""

SALES_BY_CUSTOMER_SEGMENT = """
SELECT c.segment, COUNT(*) AS orders, SUM(f.total_amount) AS revenue
FROM dbo.fact_sales f
JOIN dbo.dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.segment
ORDER BY revenue DESC;
"""

MONTHLY_REVENUE = """
SELECT d.[year], d.month_name, SUM(f.total_amount) AS revenue
FROM dbo.fact_sales f
JOIN dbo.dim_date d ON d.date_key = f.date_key
GROUP BY d.[year], d.[month], d.month_name
ORDER BY d.[year], MIN(d.[month]);
"""
