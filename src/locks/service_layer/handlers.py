from src.locks.domain.model import Lock
from . import unit_of_work


class LockNotExists(Exception):
    pass


class AlreadyAcquired(Exception):
    pass


async def add_lock(name: str, uow: unit_of_work.AsyncSqlUnitOfWork):
    async with uow:
        lock = await uow.locks.get(name)
        if not lock:
            lock = Lock(name=name, is_locked=False)
            await uow.locks.create_or_none(lock)

        await uow.commit()


async def acquire(name: str, uow: unit_of_work.AsyncSqlUnitOfWork):
    async with uow:
        lock = await uow.locks.get(name)
        if not lock:
            raise LockNotExists()

        if lock.is_locked:
            raise AlreadyAcquired(f'Lock {lock.name} already acquired.')

        lock.is_locked = True
        await uow.locks.update(lock)
        await uow.commit()


async def release(name: str, uow: unit_of_work.AsyncSqlUnitOfWork):
    async with uow:
        lock = await uow.locks.get(name)
        if not lock:
            raise LockNotExists()

        lock.is_locked = False
        await uow.locks.update(lock)
        await uow.commit()
