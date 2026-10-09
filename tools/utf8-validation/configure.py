"""Generate a disposable SQL test configuration without printing credentials."""
import json
import os
from pathlib import Path

password = os.environ["SQL_TEST_PASSWORD"]
connection = (
    "Server=127.0.0.1,1433;Database=master;User ID=sa;"
    f"Password={password};Encrypt=False;TrustServerCertificate=True;Pooling=False"
)
configuration = {
    "TCPConnectionString": connection,
    # The shared test gate requires both entries. These focused tests use only TCP;
    # Named Pipes is not available on Linux.
    "NPConnectionString": connection,
    "SupportsIntegratedSecurity": False,
    "ManagedIdentitySupported": False,
    "EnclaveEnabled": False,
    "TracingEnabled": False,
}
path = Path(os.environ["TEST_MDS_CONFIG"])
path.write_text(json.dumps(configuration), encoding="utf-8")
path.chmod(0o600)
print("Configured the six UTF-8 regression cases against the temporary SQL Server.")
