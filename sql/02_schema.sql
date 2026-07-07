-- Fabric-like retail star schema. Idempotent: safe to re-run.
USE [$(DbName)];
GO

IF OBJECT_ID(N'dbo.fact_sales', N'U')   IS NOT NULL DROP TABLE dbo.fact_sales;
IF OBJECT_ID(N'dbo.dim_customer', N'U') IS NOT NULL DROP TABLE dbo.dim_customer;
IF OBJECT_ID(N'dbo.dim_product', N'U')  IS NOT NULL DROP TABLE dbo.dim_product;
IF OBJECT_ID(N'dbo.dim_date', N'U')     IS NOT NULL DROP TABLE dbo.dim_date;
GO

CREATE TABLE dbo.dim_date (
    date_key    INT           NOT NULL PRIMARY KEY,   -- yyyymmdd
    [date]      DATE          NOT NULL,
    [year]      SMALLINT      NOT NULL,
    [quarter]   TINYINT       NOT NULL,
    [month]     TINYINT       NOT NULL,
    month_name  VARCHAR(20)   NOT NULL
);
GO

CREATE TABLE dbo.dim_customer (
    customer_key  INT           NOT NULL PRIMARY KEY,
    customer_name NVARCHAR(100) NOT NULL,
    segment       VARCHAR(20)   NOT NULL,
    country       VARCHAR(50)   NOT NULL
);
GO

CREATE TABLE dbo.dim_product (
    product_key  INT           NOT NULL PRIMARY KEY,
    product_name NVARCHAR(100) NOT NULL,
    category     VARCHAR(50)   NOT NULL,
    unit_price   DECIMAL(10,2) NOT NULL
);
GO

CREATE TABLE dbo.fact_sales (
    sale_id       BIGINT        NOT NULL PRIMARY KEY,
    date_key      INT           NOT NULL REFERENCES dbo.dim_date(date_key),
    customer_key  INT           NOT NULL REFERENCES dbo.dim_customer(customer_key),
    product_key   INT           NOT NULL REFERENCES dbo.dim_product(product_key),
    quantity      INT           NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL,
    total_amount  DECIMAL(12,2) NOT NULL
);
GO
