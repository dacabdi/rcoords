'''
location provider based request and response parsers
'''

from abc import ABC, abstractmethod
from typing import Dict

class IClient(ABC):
    '''
    location provider client
    '''

    @abstractmethod
    async def request(self, data: Dict) -> str:
        '''
        requests from a location provider using a query dictionary
        '''

class PtvClient(IClient):
    '''
    ptv location provider client
    '''

    BASE_URL = 'https://api.myptv.com/geocoding/v1/locations/by-text'
    HTTP_METHOD = 'GET'
    API_KEY_HEADER_NAME = 'apiKey'

    def __init__(self, http_client, apikey):
        self._http_client = http_client
        self._apikey = apikey
        self._headers = {self.API_KEY_HEADER_NAME : self._apikey}

    async def request(self, data: Dict) -> str:
        '''
        requests from a location provider using a query dictionary
        '''
        res = await self._http_client.request(
            self.HTTP_METHOD,
            self.BASE_URL,
            headers=self._headers,
            params=data,)
        res.raise_for_status()
        return res.text

class GoogleClient(IClient):
    '''
    google maps location provider client
    '''

    BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    HTTP_METHOD = 'GET'
    API_KEY_FIELD = 'key'

    def __init__(self, http_client, apikey):
        self._http_client = http_client
        self._apikey = apikey
        self._apiKeyReq = {self.API_KEY_FIELD : apikey}

    async def request(self, data: Dict) -> str:
        '''
        requests from a location provider using a query dictionary
        '''
        res = await self._http_client.request(
            self.HTTP_METHOD,
            self.BASE_URL,
            params=data | self._apiKeyReq,)
        res.raise_for_status()
        return res.text

class BingClient(IClient):
    '''
    bing maps location provider client
    '''

    BASE_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    HTTP_METHOD = 'GET'
    API_KEY_FIELD = 'key'

    def __init__(self, http_client, apikey):
        self._http_client = http_client
        self._apikey = apikey
        self._apiKeyReq = {self.API_KEY_FIELD : apikey}

    async def request(self, data: Dict) -> str:
        '''
        requests from a location provider using a query dictionary
        '''
        res = await self._http_client.request(
            self.HTTP_METHOD,
            self.BASE_URL,
            params=data | self._apiKeyReq,)
        res.raise_for_status()
        return res.text
