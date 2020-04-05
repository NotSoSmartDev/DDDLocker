import asyncpg
import sqlalchemy

from fastapi import FastAPI, Body, Depends, status, Response

from . import views
from .locks.adapters.orm import metadata
from .locks.service_layer import handlers
from .locks.service_layer.unit_of_work import AsyncSqlUnitOfWork

DSN = 'postgresql://test:test@0.0.0.0:5436/test'

api = FastAPI()


@api.on_event('startup')
async def startup():
    engine = sqlalchemy.create_engine(DSN)
    metadata.create_all(engine)

    api.state.db_pool = await asyncpg.create_pool(DSN)


async def get_uow():
    async with api.state.db_pool.acquire() as conn:
        yield AsyncSqlUnitOfWork(conn)


@api.post('/locks', status_code=status.HTTP_201_CREATED)
async def create_lock(name: str = Body(..., embed=True), uow=Depends(get_uow)):
    await handlers.add_lock(name, uow)


@api.post('/locks/{name}/acquire', status_code=status.HTTP_200_OK)
async def acquire_lock(name: str, uow=Depends(get_uow)):
    try:
        await handlers.acquire(name, uow)
    except handlers.LockNotExists:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@api.post('/locks/{name}/release', status_code=status.HTTP_200_OK)
async def release_lock(name: str, uow=Depends(get_uow)):
    try:
        await handlers.release(name, uow)
    except handlers.LockNotExists:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@api.get('/locks/{name}')
async def lock_info(name: str, uow=Depends(get_uow)):
    lock = await views.get_lock(name, uow)

    if not lock:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return lock
