import importlib

import pytest
from fastapi.testclient import TestClient


def configure_test_environment(monkeypatch: pytest.MonkeyPatch, tmp_path):
    database_path = tmp_path / "newsalpha-test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("ENABLE_MOCK_SEED_ON_STARTUP", "false")
    monkeypatch.setenv("NEWS_PROVIDER_MODE", "mock")
    monkeypatch.setenv("MARKET_DATA_PROVIDER_MODE", "mock")

    from app.core.config import get_settings
    from app.db.session import get_engine, get_session_factory

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    return get_engine, get_session_factory


@pytest.fixture()
def db_session(monkeypatch: pytest.MonkeyPatch, tmp_path):
    _, get_session_factory = configure_test_environment(monkeypatch, tmp_path)

    from app.db.init_db import init_db
    from app.services.pipeline.seed import SeedService

    init_db(drop_all=True)
    session = get_session_factory()()
    SeedService().seed_all(session, force_reset=True)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path):
    get_engine, get_session_factory = configure_test_environment(monkeypatch, tmp_path)

    from app.db.init_db import init_db
    from app.services.pipeline.seed import SeedService

    init_db(drop_all=True)
    session = get_session_factory()()
    SeedService().seed_all(session, force_reset=True)
    session.close()

    import app.main as main_module

    importlib.reload(main_module)
    with TestClient(main_module.app) as test_client:
        yield test_client

    get_engine().dispose()
