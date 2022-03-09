# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import asyncio
import unittest
from unittest.mock import Mock

from rcoords.asyncext import run_sync
from rcoords.client import PtvClient

from test.async_utils import wait_for_condition, notify_condition

class StubResponse():

    def __init__(self, text=None, throw=None):
        self.text = text
        self.status_calls = 0
        self._throw = throw

    def raise_for_status(self):
        self.status_calls += 1
        if self._throw:
            raise self._throw

class StubAsyncHttpClient():

    def __init__(self):
        self.calls = []
        self.response = None
        self._condition = asyncio.Condition()

    async def request(self, method, url, headers={}, params={}):
        self.calls.append({
            'method' : method,
            'url' : url,
            'headers' : headers,
            'params' : params,})
        await wait_for_condition(self._condition)
        return self.response

    async def respond(self, response):
        self.response = response
        await notify_condition(self._condition)

class test_PvtClient(unittest.TestCase):

    def test_successful_query(self):
        http_client = StubAsyncHttpClient()
        response = StubResponse(text='wait for godot')
        client = PtvClient(http_client, 'MY_API_KEY')

        self.assertEqual(0, len(http_client.calls), msg='because no request has been made')
        self.assertEqual(0, response.status_calls, msg='because status shouldn\'t have been check')

        loop = asyncio.get_event_loop()
        task = loop.create_task(client.request({'prop1':'val1','prop2':'val2'}))
        self.assertFalse(task.done(), msg='because it is still waiting on response from underlying http client')

        # respond and release the wait condition
        run_sync(http_client.respond(response))

        self.assertTrue(task.done(), 'because the http client responded successfully')
        self.assertEqual(1, len(http_client.calls), msg='because request was filed')
        self.assertDictEqual({'method' : 'GET',
            'url' : 'https://api.myptv.com/geocoding/v1/locations/by-text',
            'headers' : {'apiKey' : 'MY_API_KEY'},
            'params' : {'prop1':'val1','prop2':'val2'}},
            http_client.calls[0],
            msg='because request fields must match'),
        self.assertEqual(1, response.status_calls, msg='because status should have been check')
        self.assertEqual('wait for godot', task.result(), msg='because response must match')

    def test_failed_query(self):
        http_client = StubAsyncHttpClient()
        response = StubResponse(text='wait for godot', throw=RuntimeError('something happened!'))
        client = PtvClient(http_client, 'MY_API_KEY')

        self.assertEqual(0, len(http_client.calls), msg='because no request has been made')
        self.assertEqual(0, response.status_calls, msg='because status shouldn\'t have been check')

        loop = asyncio.get_event_loop()
        task = loop.create_task(client.request({'prop1':'val1','prop2':'val2'}))
        self.assertFalse(task.done(), msg='because it is still waiting on response from underlying http client')

        # respond and release the wait condition
        run_sync(http_client.respond(response))

        self.assertTrue(task.done(), 'because the http client responded')
        self.assertEqual(1, len(http_client.calls), msg='because request was filed')
        self.assertDictEqual({'method' : 'GET',
            'url' : 'https://api.myptv.com/geocoding/v1/locations/by-text',
            'headers' : {'apiKey' : 'MY_API_KEY'},
            'params' : {'prop1':'val1','prop2':'val2'}},
            http_client.calls[0],
            msg='because request fields must match'),
        self.assertEqual(1, response.status_calls, msg='because status should have been check')

        with self.assertRaises(RuntimeError) as context:
            task.result()

        self.assertEqual(('something happened!',), context.exception.args)
