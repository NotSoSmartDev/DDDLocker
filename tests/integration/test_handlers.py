import asyncio

import pytest

from src.locks.service_layer import handlers
from src.locks.service_layer.unit_of_work import AsyncSqlUnitOfWork


@pytest.mark.asyncio
async def test_can_create_lock(db_conn):
    uow = AsyncSqlUnitOfWork(db_conn)

    await handlers.add_lock('Test', uow)

    async with uow:
        lock = await uow.locks.get('Test')

    assert (lock.name, lock.is_locked) == ('Test', False)


@pytest.mark.asyncio
async def test_concurrent_create_lock(conn_factory):
    async def add_lock():
        async with conn_factory.acquire() as conn:
            return await handlers.add_lock('Test', AsyncSqlUnitOfWork(conn))

    cors = [add_lock(), add_lock()]
    res1, res2 = await asyncio.gather(*cors, return_exceptions=True)

    assert not isinstance(res1, Exception)
    assert not isinstance(res2, Exception)


@pytest.mark.asyncio
async def test_acquired_set_lock_locked(db_conn):
    uow = AsyncSqlUnitOfWork(db_conn)

    await handlers.add_lock('Test', uow)
    await handlers.acquire('Test', uow)

    async with uow:
        lock = await uow.locks.get('Test')

    assert lock.is_locked


@pytest.mark.asyncio
async def test_concurrent_acquired_success_only_once(conn_factory):
    db_conn = await conn_factory.acquire()
    await handlers.add_lock('Test', AsyncSqlUnitOfWork(db_conn))

    async def acquire():
        async with conn_factory.acquire() as conn:
            return await handlers.acquire('Test', AsyncSqlUnitOfWork(conn))

    cors = [acquire(), acquire()]
    res = await asyncio.gather(*cors, return_exceptions=True)

    async with AsyncSqlUnitOfWork(db_conn) as uow:
        lock = await uow.locks.get('Test')

    await conn_factory.release(db_conn)

    assert lock.is_locked
    assert len([_ for _ in res if isinstance(_, handlers.AlreadyAcquired)]) == 1


@pytest.mark.asyncio
async def test_release_set_lock_unlocked(db_conn):
    uow = AsyncSqlUnitOfWork(db_conn)

    await handlers.add_lock('Test', uow)
    await handlers.acquire('Test', uow)
    await handlers.release('Test', uow)

    async with uow:
        lock = await uow.locks.get('Test')

    assert not lock.is_locked
