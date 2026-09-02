import asyncio
import nest_asyncio


def run_async_sync(coro):
    """Safely execute an async coroutine from a synchronous context,
    supporting environments where an event loop is already running.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)
