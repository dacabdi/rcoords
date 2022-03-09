'''
provider based request and response parsers
'''
import json

from abc import ABC, abstractmethod
from typing import Dict, List

from .models import Coordinate

class IReqParser(ABC):
    '''
    location provider request parser
    '''

    @abstractmethod
    def parse(self, address) -> Dict:
        '''
        parses an address into a request dictionary
        '''

class IRespParser(ABC):
    '''
    location provider response parser
    '''

    @abstractmethod
    def parse(self, response) -> List[Coordinate]:
        '''
        parses a provider response into a list of coordinates
        '''

class PlainReqParser(IReqParser):
    '''
    converts an address into a plain test request object
    '''

    def __init__(self, field_name, common=None):
        self._field_name = field_name
        self._common = common if common else {}

    def parse(self, address) -> Dict:
        '''
        parses an address into a plain text request object
        '''
        return {self._field_name : address} | self._common

class PtvRespParser(IRespParser):

    def parse(self, response) -> List[Coordinate]:
        '''
        parses a provider response into a list of coordinates
        '''
        # TODO clean up
        response = json.loads(response)
        locations = sorted(response['locations'], key=lambda d: d['quality']['totalScore'], reverse=True)
        return [Coordinate(latitude=loc['referencePosition']['latitude'], longitude=loc['referencePosition']['longitude']) for loc in locations]

class GoogleRespParser(IRespParser):

    def parse(self, response) -> List[Coordinate]:
        '''
        parses a provider response into a list of coordinates
        '''
        # TODO clean up
        response = json.loads(response)
        results = response['results']
        return [Coordinate(latitude=r['geometry']['location']['lat'], longitude=r['geometry']['location']['lng']) for r in results]

class BingRespParser(IRespParser):

    def parse(self, response) -> List[Coordinate]:
        '''
        parses a provider response into a list of coordinates
        '''
        # TODO clean up
        response = json.loads(response)
        result = []
        for rset in response['resourceSets']:
            for resource in rset['resources']:
                coord = resource['point']['coordinates']
                result.append(Coordinate(latitude=coord[0], longitude=coord[1]))
        return result