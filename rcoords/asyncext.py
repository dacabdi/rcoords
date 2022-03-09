'''
asyncio extensions
'''

import asyncio
from typing import Coroutine

async def loop_forever_async(coro: Coroutine, *args, **kwargs):
    '''
    runs a couroutine on an infinite loop
    '''
    while True:
        await coro(*args, **kwargs)

def run_sync_with_loop(loop, coro: Coroutine, timeout=1):
    '''
    run sync on provided event loop with timeout
    '''
    return loop.run_until_complete(asyncio.wait_for(coro, timeout))

def run_sync(coro: Coroutine, timeout=1):
    '''
    run sync on main event loop with timeout
    '''
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return run_sync_with_loop(loop, coro, timeout)
