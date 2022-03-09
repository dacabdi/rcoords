# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
import asyncio
import asynctest

from rcoords.asyncext import run_sync, loop_forever_async
from test.async_utils import wait_for_condition, notify_condition

class test_AsyncExtFunctions(unittest.TestCase):

    def test_sync_run(self):
        coro = asynctest.CoroutineMock()

        run_sync(coro())

        self.assertTrue(asyncio.iscoroutinefunction(coro))
        coro.assert_called_once()
        coro.assert_awaited()

    def test_loop_forever_async(self):
        loop = asyncio.get_event_loop()
        cond = asyncio.Condition()
        coro = asynctest.CoroutineMock(side_effect=lambda x, y, some_arg: wait_for_condition(cond))
        task = loop.create_task(loop_forever_async(coro, 1, 2, some_arg="test"))

        run_sync(notify_condition(cond))
        self.assertFalse(task.done())
        self.assertEqual(coro.await_count, 1)
        coro.assert_called_with(1, 2, some_arg="test")

        run_sync(notify_condition(cond))
        self.assertFalse(task.done())
        self.assertEqual(coro.await_count, 2)

        run_sync(notify_condition(cond))
        self.assertFalse(task.done())
        self.assertEqual(coro.await_count, 3)

        task.cancel()
        run_sync(notify_condition(cond))
        self.assertTrue(task.done())
        # NOTE calling cancellation does not guarantee that the task
        #  is cancelled immediately. the coroutine has, still, been awaited
        self.assertEqual(coro.await_count, 4)

        run_sync(notify_condition(cond))
        self.assertEqual(coro.await_count, 4)

    def test_loop_forever_async_cancels_on_coro_cancelled(self):
        coro = asynctest.CoroutineMock(side_effect=ValueError)

        with self.assertRaises(ValueError):
            run_sync(loop_forever_async(coro))
