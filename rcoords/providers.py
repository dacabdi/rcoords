'''
location resolver provider
'''

from abc import ABC, abstractmethod
from typing import List

from .models import Coordinate
from .parsers import IReqParser, IRespParser
from .client import IClient

class IProvider(ABC):
    '''
    location provider contract
    '''

    @abstractmethod
    async def query(self, address) -> List[Coordinate]:
        '''
        obtains the coordinates for an address
        '''

    @property
    @abstractmethod
    def tag(self) -> str:
        '''
        tags providers
        '''

class GenericProvider(IProvider):
    '''
    location provider based
    '''

    def __init__(self, client: IClient, req_parser: IReqParser, resp_parser: IRespParser, tag: str):
        self._client = client
        self._req_parser = req_parser
        self._resp_parser = resp_parser
        self._tag = tag

    async def query(self, address) -> List[Coordinate]:
        req = self._req_parser.parse(address)
        raw = await self._client.request(req)
        res = self._resp_parser.parse(raw)
        return res

    @property
    def tag(self):
        return self._tag
