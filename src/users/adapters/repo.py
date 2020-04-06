import asyncpg

from ..domain.model import User


class AsyncSqlRepo:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create_or_none(self, user: User):
        await self.conn.execute(
            "INSERT INTO users(id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user.id_,
            user.username,
        )
