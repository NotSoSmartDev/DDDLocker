import pytest

import asyncpg
import sqlalchemy

from src.api import DSN
from src.locks.adapters.orm import metadata


@pytest.fixture(autouse=True)
def make_schema():
    engine = sqlalchemy.create_engine(DSN)
    metadata.create_all(engine)

    yield

    metadata.drop_all(engine)


@pytest.fixture
async def conn_factory() -> asyncpg.pool.Pool:
    async with asyncpg.create_pool(DSN) as conn_factory:
        yield conn_factory


@pytest.fixture
async def db_conn() -> asyncpg.Connection:
    conn = await asyncpg.connect(DSN)

    tr = conn.transaction()
    await tr.start()
    try:
        yield conn
    finally:
        await tr.rollback()
