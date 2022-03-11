'''
provider based response verifiers
'''
import json
import structlog

from abc import ABC, abstractmethod
from typing import Dict, List

from .events import AppEvent
from .models import Address, Coordinate

logger = structlog.get_logger('rcoords')

class IRespVerifier(ABC):
    '''
    location provider response parser
    '''

    @abstractmethod
    def verify(self, address, response) -> str:
        '''
        verifies the correctness of a provider response
        '''

class GenericRespVerifier(IRespVerifier):

    def __init__(self, provider: str):
        self._provider = provider


    def verify(self, address, coordsAndAddr) -> str:
        '''
        verifies the correctness of the response
        '''
        # TODO clean up
        verifiedLocs = []
        for loc in coordsAndAddr:
            if  loc.address.lower().startswith(address.lower()):
                verifiedLocs.append(loc)
                logger.info(AppEvent(f"Verifier approved a '{self._provider}' location for '{address}'"))
            else:
                logger.warn(AppEvent(f"Verifier dismissed a '{self._provider}' location for '{address}', got: '{loc.address}'"))

        return verifiedLocs

# class GoogleRespVerifier(IRespVerifier):

#     def verify(self, address, response) -> str:
#         '''
#         verifies the correctness of the response
#         '''
#         # TODO clean up
#         response = json.loads(response)
#         verifiedLocs = []
#         for loc in response['results']:
#             if loc['formatted_address'].lower().startswith(address.lower()):
#                 verifiedLocs.append(loc)
#                 logger.info(AppEvent(f"Verifier approved a Google location for '{address}'"))
#             else:
#                 logger.warn(AppEvent(f"Verifier dismissed a Google location for '{address}', got: '{loc['formatted_address']}'"))

#         response['results'] = verifiedLocs
#         return json.dumps(response)

# class BingRespVerifier(IRespVerifier):

#     def verify(self, address, response) -> str:
#         '''
#         verifies the correctness of the response
#         '''
#         # TODO clean up
#         response = json.loads(response)
#         verifiedRSets = []
#         for rSet in response['resourceSets']:
#             verifiedResources = []
#             for resource in rSet['resources']:
#                 if resource['address']['formattedAddress'].lower().startswith(address.lower()):
#                     verifiedResources.append(resource)
#                     logger.info(AppEvent(f"Verifier approved a Bing location for '{address}'"))
#                 else:
#                     logger.warn(AppEvent(f"Verifier dismissed a Bing location for '{address}', got: '{loc['address']['formattedAddress']}'"))
#             rSet['resources'] = verifiedResources
#             verifiedRSets.append(rSet)

#         response['resourceSets'] = verifiedRSets
#         return json.dumps(response)