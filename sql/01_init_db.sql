-- Create the warehouse database. The name comes from the DbName sqlcmd variable
-- (defaults to fabric_mock; set MS_FABRIC_DB to match your real Fabric DB name so
-- queries are identical against local and cloud). Idempotent.
IF DB_ID(N'$(DbName)') IS NULL
BEGIN
    CREATE DATABASE [$(DbName)];
END
GO
