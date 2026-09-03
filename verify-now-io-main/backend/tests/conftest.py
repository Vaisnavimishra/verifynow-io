import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.models import Base
from app.db.session import get_db


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def app(db_session_factory, monkeypatch):
    # Avoid touching real Redis/Kafka in unit tests.
    from app.services import cache as cache_module
    from app.services import kafka_bus as kafka_module

    async def fake_check_rate_limit(client_key):
        return True, 100

    async def fake_get_cached_result(_hash):
        return None

    async def fake_set_cached_result(_hash, _result):
        return None

    async def fake_publish_verification_task(request_id):
        # In tests we process synchronously instead of going through Kafka.
        from app.services.pipeline import process_verification_request

        async with db_session_factory() as session:
            await process_verification_request(request_id, session)

    monkeypatch.setattr(cache_module, "check_rate_limit", fake_check_rate_limit)
    monkeypatch.setattr(cache_module, "get_cached_result", fake_get_cached_result)
    monkeypatch.setattr(cache_module, "set_cached_result", fake_set_cached_result)
    monkeypatch.setattr(kafka_module, "publish_verification_task", fake_publish_verification_task)

    from app.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    settings.KAFKA_ENABLED = True  # exercised via the faked publish above

    from app.main import app as fastapi_app

    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Note: ASGITransport (used by the test client) does not invoke lifespan
    # events, so app.main's startup (which creates tables on the real
    # Postgres engine) never runs here -- the sqlite test schema created in
    # test_engine is what's actually used.

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
