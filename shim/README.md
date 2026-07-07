# Local Fabric shim — zero client-side changes

Your app's Fabric connection builder hardcodes a **real Fabric** connection string:

```
Encrypt=Yes; TrustServerCertificate=No;
Authentication=ActiveDirectoryServicePrincipal; UID=<client_id>; PWD=<client_secret>
```

A local SQL Server cannot satisfy that string:
- `TrustServerCertificate=No` rejects the mock's self-signed cert, **and**
- `Authentication=ActiveDirectoryServicePrincipal` makes the ODBC driver fetch a real Entra
  token from `login.microsoftonline.com` — fake creds can't mint one, and box SQL Server has
  no Entra integration to accept one. **No server-only fix can change this.**

So the string must be rewritten *before* it reaches the driver — done here by a runtime shim,
**without editing any app source**.

## How it works
Python auto-imports `sitecustomize` at interpreter startup if it's on `PYTHONPATH`. This
`sitecustomize.py` wraps `pyodbc.connect` and, **only when the Server host is localhost**,
rewrites the outgoing string to plain SQL auth against the docker mock:
strip `Authentication`, force `TrustServerCertificate=Yes`, swap `UID`/`PWD` for `sa` + the
mock password. **Real-Fabric (non-localhost) connections pass through completely untouched.**

## Activate (local dev only)
Point your app's Fabric connection at `localhost:1433` (any tenant/client/secret values), make
sure `make up && make seed` has run, then start the app with these env vars:

```bash
export PYTHONPATH=/Users/sukeesh/workspace/sukeesh/fabric-local/shim:$PYTHONPATH
export FABRIC_LOCAL_MOCK=1
export FABRIC_LOCAL_SA_PASSWORD='LocalFabric_123!'   # must match docker .env SA_PASSWORD
# optional: export FABRIC_LOCAL_SA_USER=sa
```

You'll see `[fabric-local-shim] localized connection to mock (SQL auth)` on stderr for each
local connection. Deactivate by unsetting `FABRIC_LOCAL_MOCK` (or dropping the PYTHONPATH entry) —
nothing in your repo changed, so there's nothing to revert.

## Caveats
- Only rewrites connections whose `Server` host is `localhost`/`127.0.0.1`/`0.0.0.0`/`::1`.
- The mock is a real SQL Server, so standard T-SQL is identical; Fabric-only features
  (`COPY INTO` from OneLake, cross-warehouse queries) have no local equivalent.
