import os
from pathlib import Path

_VAULT_PATH = "/vault/secrets/.env"
_LOCAL_PATH = str(Path(__file__).parents[3] / ".env")

VAULT_ENV_FILE = _VAULT_PATH if os.path.exists(_VAULT_PATH) else _LOCAL_PATH
