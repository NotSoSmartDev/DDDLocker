import abc
from typing import Optional

import asyncpg

from src.locks.domain.model import Lock


class AbstractRepo(abc.ABC):
    @abc.abstractmethod
    async def get(self, name: str) -> Optional[Lock]:
        raise NotImplemented

    @abc.abstractmethod
    async def create_or_none(self, lock: Lock):
        raise NotImplemented


class AsyncSqlRepo(AbstractRepo):
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get(self, name: str) -> Optional[Lock]:
        row = await self.conn.fetchrow(
            'SELECT * FROM locks WHERE name=$1 FOR UPDATE', name,
        )
        if not row:
            return None

        return Lock(name=row['name'], is_locked=row['is_locked'])

    async def create_or_none(self, lock: Lock):
        await self.conn.execute(
            'INSERT INTO locks(name, is_locked) VALUES ($1, $2) ON CONFLICT DO NOTHING',
            lock.name, lock.is_locked,
        )

    async def update(self, lock: Lock):
        await self.conn.execute(
            'UPDATE locks set is_locked=$1 WHERE name=$2',
            lock.is_locked, lock.name,
        )
