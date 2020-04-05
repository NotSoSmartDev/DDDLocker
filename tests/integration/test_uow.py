import pytest

from src.locks.domain.model import Lock
from src.locks.service_layer import unit_of_work


@pytest.mark.asyncio
async def test_can_retrieve_lock(db_conn):
    await db_conn.execute(
        "INSERT INTO locks(name, is_locked) VALUES($1, $2)", "Test", False,
    )

    uow = unit_of_work.AsyncSqlUnitOfWork(db_conn)

    async with uow:
        lock = await uow.locks.get("Test")
        await uow.commit()

    assert (lock.name, lock.is_locked) == ("Test", False)


@pytest.mark.asyncio
async def test_can_add_lock(db_conn):
    uow = unit_of_work.AsyncSqlUnitOfWork(db_conn)

    lock = Lock("Test", False)
    async with uow:
        await uow.locks.create_or_none(lock)
        await uow.commit()

    [row] = await db_conn.fetch("SELECT * FROM locks")

    assert (row["name"], row["is_locked"]) == (lock.name, lock.is_locked)
