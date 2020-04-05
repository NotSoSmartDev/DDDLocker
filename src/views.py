from typing import Optional

from .locks.service_layer.unit_of_work import AsyncSqlUnitOfWork


async def get_lock(name: str, uow: AsyncSqlUnitOfWork) -> Optional[dict]:
    async with uow:
        row = await uow.conn.fetchrow(
            'SELECT * FROM locks WHERE name=$1', name,
        )
        await uow.commit()

    if not row:
        return

    return {
        'name': row['name'],
        'is_locked': row['is_locked'],
    }
