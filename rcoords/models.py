'''
data models
'''

from __future__ import annotations # resolve class self reference

import math
from dataclasses import dataclass

@dataclass
class Address:
    '''
    model for address
    '''
    number: str = ''
    street: str = ''
    city: str = ''
    postal: str = ''
    state: str = ''
    country: str = 'United States'

    def __str__(self) -> str:
        return f'{self.number} {self.street}, {self.city}, {self.state} {self.postal}'

@dataclass
class Coordinate:
    '''
    model for coordinate
    '''
    latitude: float = 0
    longitude: float = 0

    def distance(self, other: Coordinate) -> float:
        return math.sqrt(
            (self.latitude  - other.latitude ) ** 2
          + (self.longitude - other.longitude) ** 2)

    def __str__(self) -> str:
        return f'(lat={self.latitude}, lon={self.longitude})'

    def __repr__(self) -> str:
        return str(self)