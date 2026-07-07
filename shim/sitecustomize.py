"""Local-only pyodbc shim: make the real app talk to the local Fabric mock
WITHOUT editing any app source.

Python auto-imports `sitecustomize` at interpreter startup if it's on
PYTHONPATH. So you activate this purely with an env var when running locally:

    export PYTHONPATH=/Users/sukeesh/workspace/sukeesh/fabric-local/shim:$PYTHONPATH
    export FABRIC_LOCAL_MOCK=1
    export FABRIC_LOCAL_SA_PASSWORD='LocalFabric_123!'   # matches docker .env
    # (optional) export FABRIC_LOCAL_SA_USER=sa

The app keeps building its real Fabric connection string
(Encrypt=Yes; TrustServerCertificate=No; Authentication=ActiveDirectoryServicePrincipal;
UID=<client_id>; PWD=<client_secret>). This shim wraps pyodbc.connect and, ONLY when
the Server host is local, rewrites it to plain SQL auth against the docker mock:

  * drop  Authentication=ActiveDirectoryServicePrincipal   (no Entra round-trip)
  * set   TrustServerCertificate=Yes                       (self-signed dev cert)
  * swap  UID/PWD  ->  sa / $FABRIC_LOCAL_SA_PASSWORD

Non-local (real Fabric) connections are passed through completely untouched.
Deactivate by unsetting FABRIC_LOCAL_MOCK (or removing the PYTHONPATH entry).
"""
import os

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def _host_of(server_value: str) -> str:
    """Extract bare host from an ODBC Server value: host / host,port / host:port / tcp:host,port."""
    v = server_value.strip()
    if v.lower().startswith("tcp:"):
        v = v[4:]
    v = v.split(",", 1)[0]      # drop ,port
    v = v.rsplit(":", 1)[0] if v.count(":") == 1 else v  # drop :port (but keep bare ipv6-less host)
    return v.strip().strip("[]").lower()


def _is_local(conn_str: str) -> bool:
    for part in conn_str.split(";"):
        k, _, val = part.partition("=")
        if k.strip().lower() in ("server", "addr", "address", "network address"):
            return _host_of(val) in _LOCAL_HOSTS
    return False


def _localize(conn_str: str) -> str:
    sa_user = os.environ.get("FABRIC_LOCAL_SA_USER", "sa")
    sa_pwd = os.environ.get("FABRIC_LOCAL_SA_PASSWORD", "")
    kept = []
    for part in conn_str.split(";"):
        if not part.strip():
            continue
        key = part.split("=", 1)[0].strip().lower()
        if key in ("authentication", "uid", "pwd", "trustservercertificate"):
            continue  # we re-add our own auth below
        kept.append(part)
    kept.append("TrustServerCertificate=Yes")
    kept.append(f"UID={sa_user}")
    kept.append(f"PWD={sa_pwd}")
    return ";".join(kept)


def _install():
    if os.environ.get("FABRIC_LOCAL_MOCK", "").lower() not in ("1", "true", "yes"):
        return
    try:
        import pyodbc
    except Exception:
        return
    if getattr(pyodbc.connect, "_fabric_local_shim", False):
        return

    _real_connect = pyodbc.connect

    def connect(*args, **kwargs):
        if args and isinstance(args[0], str) and _is_local(args[0]):
            new = _localize(args[0])
            # A real Entra token supplied via attrs_before would override SQL auth — drop it.
            attrs = kwargs.get("attrs_before")
            if isinstance(attrs, dict) and 1256 in attrs:  # SQL_COPT_SS_ACCESS_TOKEN
                attrs = {k: v for k, v in attrs.items() if k != 1256}
                kwargs["attrs_before"] = attrs
            import sys
            print("[fabric-local-shim] localized connection to mock (SQL auth)", file=sys.stderr)
            args = (new,) + args[1:]
        return _real_connect(*args, **kwargs)

    connect._fabric_local_shim = True
    pyodbc.connect = connect


_install()
