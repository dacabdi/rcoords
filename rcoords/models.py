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
    quadrant: str = ''
    street: str = ''
    street_class: str = ''
    city: str = ''
    postal: str = ''
    state: str = ''
    country: str = 'United States'

    def __str__(self) -> str:
        leading = ' '.join([
            field for field in [
            self.number,
            self.quadrant,
            self.street,
            self.street_class]
            if field != ''])
        return f"{leading}, {self.city}, {self.state} {self.postal}"

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
        return f'{self.latitude}, {self.longitude}'

    def __repr__(self) -> str:
        return str(self)