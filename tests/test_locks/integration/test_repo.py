import pytest

from src.locks.adapters.repo import AsyncSqlRepo
from src.locks.domain.model import Lock


@pytest.mark.asyncio
async def test_can_add_lock(db_conn):
    lock = Lock("Test", False)

    repo = AsyncSqlRepo(db_conn)
    await repo.create_or_none(lock)

    [row] = await db_conn.fetch("SELECT * FROM locks WHERE name=$1", lock.name,)

    assert (row["name"], row["is_locked"]) == (lock.name, lock.is_locked)


@pytest.mark.asyncio
async def test_can_get_lock(db_conn):
    await db_conn.execute(
        "INSERT INTO locks(name, is_locked) VALUES ($1, $2)", "Test", False,
    )

    repo = AsyncSqlRepo(db_conn)
    lock = await repo.get("Test")

    assert (lock.name, lock.is_locked) == ("Test", False)
