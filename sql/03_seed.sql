-- Deterministic sample data so tests can assert exact aggregates.
USE [$(DbName)];
GO

DELETE FROM dbo.fact_sales;
DELETE FROM dbo.dim_customer;
DELETE FROM dbo.dim_product;
DELETE FROM dbo.dim_date;
GO

INSERT INTO dbo.dim_date (date_key, [date], [year], [quarter], [month], month_name) VALUES
 (20240115, '2024-01-15', 2024, 1, 1, 'January'),
 (20240220, '2024-02-20', 2024, 1, 2, 'February'),
 (20240312, '2024-03-12', 2024, 1, 3, 'March'),
 (20240418, '2024-04-18', 2024, 2, 4, 'April');
GO

INSERT INTO dbo.dim_customer (customer_key, customer_name, segment, country) VALUES
 (1, N'Contoso Ltd',     'Enterprise', 'USA'),
 (2, N'Fabrikam Inc',    'SMB',        'Germany'),
 (3, N'Northwind Traders','Enterprise','UK');
GO

INSERT INTO dbo.dim_product (product_key, product_name, category, unit_price) VALUES
 (10, N'Cloud Widget',   'Software',  120.00),
 (20, N'Data Cable',     'Hardware',   15.50),
 (30, N'Support Plan',   'Services',  500.00);
GO

INSERT INTO dbo.fact_sales (sale_id, date_key, customer_key, product_key, quantity, unit_price, total_amount) VALUES
 (1001, 20240115, 1, 10,  5, 120.00,  600.00),
 (1002, 20240115, 2, 20, 10,  15.50,  155.00),
 (1003, 20240220, 1, 30,  1, 500.00,  500.00),
 (1004, 20240312, 3, 10,  2, 120.00,  240.00),
 (1005, 20240418, 2, 20, 20,  15.50,  310.00),
 (1006, 20240418, 3, 30,  3, 500.00, 1500.00);
GO
