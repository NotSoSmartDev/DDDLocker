import asyncpg

from src.locks.adapters.repo import AsyncSqlRepo


class AsyncSqlUnitOfWork:
    locks: AsyncSqlRepo

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def __aenter__(self):
        self.tr = self.conn.transaction()
        await self.tr.start()

        self.locks = AsyncSqlRepo(self.conn)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

    async def commit(self):
        await self.tr.commit()

    async def rollback(self):
        await self.tr.rollback()
