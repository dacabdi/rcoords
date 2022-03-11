'''
data models
'''

from __future__ import annotations # resolve class self reference

import csv
import math
from typing import List

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

@dataclass
class CoordsAndAddrs:
    '''
    model for CoordsAndAddrs
    '''
    address: str
    coords: Coordinate

    def distance(self, other: CoordsAndAddrs) -> float:
        return math.sqrt(
            (self.coords.latitude  - other.coords.latitude ) ** 2
          + (self.coords.longitude - other.coords.longitude) ** 2)

    def __str__(self) -> str:
        return f'{self.coords.latitude}, {self.coords.longitude}'

    def __repr__(self) -> str:
        return str(self)

class Store:
    '''
    data store for results
    '''

    RESULTS_KEY = 'results'
    DISCREPANCY_KEY = 'discrepancy'
    ADDRESS_KEY = 'address'
    ID_KEY = 'id'
    NON_PROVIDER_FIELDS = set([ID_KEY, ADDRESS_KEY, RESULTS_KEY, DISCREPANCY_KEY])

    def __init__(self, data=None):
        self._data = data if data else {}
        self._providers = set()

    @classmethod
    def from_file(cls, file):
        '''
        creates a data store by reading a csv file
        the header of the csv file is expected to be
        (id, address, discrepancy, Provider1_lat, Provider1_lon, ..., ProviderN_lat, ProviderN_lon)
        '''
        store = Store()
        reader = csv.DictReader(file)
        for entry in reader:
            # TODO this whole parser is extremely fragile, improve this
            id = entry[cls.ID_KEY]
            pks = sorted(list(entry.keys() - cls.NON_PROVIDER_FIELDS))
            pks = [(pks[i], pks[i+1]) for i in range(0, len(pks), 2)]
            for pk in pks:
                tag = pk[0][:pk[0].index("_")]
                lat = entry[f'{tag}_lat']
                lon = entry[f'{tag}_lon']
                if lat != 'None' and lon != 'None':
                    coord = CoordsAndAddrs(address=entry[cls.ADDRESS_KEY], coords=Coordinate(latitude=float(lat), longitude=float(lon)))
                else:
                    coord = None
                store.set_result(id, tag, coord)
        return store

    def set_result(self, id, provider_tag: str, result=None):
        self._providers.add(provider_tag)
        entry = self._mint_entry(id)
        if result != None:
            entry[self.ADDRESS_KEY] = result.address
            entry[self.RESULTS_KEY][provider_tag] = result.coords
        self._update_discrepancy(entry)

    def get_result(self, id, provider_tag=None):
        if id in self._data.keys():
            results = self._data[id][self.RESULTS_KEY]
            if not provider_tag:
                return [CoordsAndAddrs(address=self._data[id][self.ADDRESS_KEY], coords=results[provider_tag]) for provider_tag in results.keys()]
            if provider_tag in results.keys():
                return CoordsAndAddrs(address=self._data[id][self.ADDRESS_KEY], coords=results[provider_tag])
        return None


    def _mint_entry(self, id):
        if id not in self._data.keys():
            self._data[id] = {
                self.ID_KEY: id,
                self.ADDRESS_KEY: '',
                self.DISCREPANCY_KEY: 0,
                self.RESULTS_KEY: {} }
        return self._data[id]

    def _update_discrepancy(self, entry):
        coords = entry[self.RESULTS_KEY].values()
        discrepancies = sorted([i.distance(j) for i in coords if i for j in coords if j and i != j], reverse=True)
        entry[self.DISCREPANCY_KEY] = 0 if len(discrepancies) == 0 else discrepancies[0]

    def __str__(self) -> str:
        '''
        serializes the store into a csv with header
        (id, discrepancy, Provider1_lat, Provider1_lon, ..., ProviderN_lat, ProviderN_lon)
        '''
        header = ','.join([self.ID_KEY, self.ADDRESS_KEY, self.DISCREPANCY_KEY] + [f'{p}_lat,{p}_lon' for p in sorted(self._providers)])
        result = [header]
        for id, v in self._data.items():
            line = [id, str('"' + v[self.ADDRESS_KEY] + '"'), str(v[self.DISCREPANCY_KEY])]
            for prov in sorted(self._providers):
                if prov in v[self.RESULTS_KEY].keys():
                    r = v[self.RESULTS_KEY][prov]
                    if r is None:
                        line += ['None', 'None']
                    else:
                        line += [str(r.latitude), str(r.longitude)]
                else:
                    line += ['None', 'None']
            result.append(','.join(line))
        return '\n'.join(result)

    def __repr__(self) -> str:
        return str(self)