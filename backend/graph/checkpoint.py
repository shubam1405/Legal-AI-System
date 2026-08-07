import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

try:
    from langgraph.store.postgres.aio import AsyncPostgresStore
except ImportError:
    AsyncPostgresStore = None  # Will try to import from somewhere else if needed, but langgraph>0.2.x should have it

__all__ = ["get_checkpointer", "get_store", "init_persistence"]

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:shubam14@localhost:5432/legal_ai")

_saver = None
_store = None
_pool = None


def _get_pool():
    """
    Constructs (but does not open) the async connection pool. Pure
    object construction — no event loop needed, safe to call at
    module-import / graph-compile time (even inside uvicorn --reload,
    where import happens while a loop is already running).
    """
    global _pool
    if _pool is None:
        from psycopg_pool import AsyncConnectionPool
        _pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0},
            open=False,
        )
    return _pool


def get_checkpointer():
    """
    Returns the AsyncPostgresSaver instance, constructed but not yet
    opened/set-up. Safe to call at graph-compile time. Actual DB
    connection + table setup happens in init_persistence(), called
    from FastAPI's startup event.
    """
    global _saver
    if _saver is None:
        _saver = AsyncPostgresSaver(_get_pool())
    return _saver


def get_store():
    global _store
    if _store is None and AsyncPostgresStore is not None:
        _store = AsyncPostgresStore(_get_pool())
    return _store


async def init_persistence() -> None:
    """
    Call once from FastAPI's startup event (i.e. from inside the actual
    running event loop uvicorn will keep using) to open the connection
    pool and run the checkpointer/store's one-time table setup.

    Must NOT be called at import time — psycopg's AsyncConnectionPool
    needs to be opened in the same loop it will be used from.
    """
    pool = _get_pool()
    if pool.closed:
        await pool.open()

    saver = get_checkpointer()
    await saver.setup()

    store = get_store()
    if store is not None:
        await store.setup()
