import importlib
import sys

import pytest
from sqlalchemy.exc import OperationalError


def reload_db_module():
    sys.modules.pop("src.core.db", None)
    return importlib.import_module("src.core.db")


def test_engine_uses_current_db_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    db = reload_db_module()

    monkeypatch.setenv("DB_HOST", "db.internal")

    db.get_engine.cache_clear()
    engine = db.get_engine()

    assert engine.url.host == "db.internal"


pytestmark = pytest.mark.anyio


async def test_create_all_tables_wraps_operational_error() -> None:
    db = reload_db_module()

    class BrokenBegin:
        async def __aenter__(self):
            raise OperationalError("SELECT 1", {}, Exception("boom"))

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    class BrokenEngine:
        def begin(self):
            return BrokenBegin()

    db.get_engine.cache_clear()
    original_get_engine = db.get_engine
    db.get_engine = lambda: BrokenEngine()

    try:
        with pytest.raises(RuntimeError, match="DB_HOST"):
            await db.create_all_tables()
    finally:
        db.get_engine = original_get_engine
