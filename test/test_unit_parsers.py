# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from ddt import ddt, data, unpack

from rcoords.models import Coordinate, CoordsAndAddrs
from rcoords.parsers import AddressRecordParser, PtvRespParser

# TODO cover failure cases
@ddt
class test_PvtRespParser(unittest.TestCase):

    @data(
        ('{"locations":[{"formattedAddress": "Address0","referencePosition":{"latitude":47.672508239746094,"longitude":-122.12815856933594},"quality":{"totalScore":90}}]}',
        [CoordsAndAddrs(address="Address0", coords=Coordinate(47.672508239746094, -122.12815856933594))]),
        ('{"locations":[{"formattedAddress": "Address1","referencePosition":{"latitude":0,"longitude":0},"quality":{"totalScore":1}},{"formattedAddress": "Address2","referencePosition":{"latitude":48.672508239746094,"longitude":-121.12815856933594},"quality":{"totalScore":89}}]}',
        [CoordsAndAddrs(address="Address2", coords=Coordinate(48.672508239746094, -121.12815856933594)),CoordsAndAddrs(address="Address1", coords=Coordinate(0, 0))])
    )
    @unpack
    def test_parse(self, input, expected):
        parser = PtvRespParser()
        result = parser.parse(input)
        self.assertEqual(expected, result)

@ddt
class test_AddressRecordParser(unittest.TestCase):

    @data(
        ({
            'Location No': '15364',
            'Quadrant': 'S',
            'Street Number/Street Name': '282',
            'Street Id': 'ST',
            'Locality': 'Homestead',
            'State': 'FL',
            'Zip Code': '330331303'
        }, '15364 S 282nd ST, Homestead, FL 33033'),
        ({
            'Location No': '15364',
            'Quadrant': 'SW',
            'Street Number/Street Name': 'FEDERAL',
            'Street Id': 'HWY',
            'Locality': 'Homestead',
            'State': 'FL',
            'Zip Code': '330331303'
        }, '15364 SW FEDERAL HWY, Homestead, FL 33033'),
        ({ # ... some entries might have the following format,
           # we handle them the best we can ...
            'Location No': '0',
            'Quadrant': '',
            'Street Number/Street Name': 'SW 284 ST & US 1',
            'Street Id': '',
            'Locality': 'Homestead',
            'State': 'FL',
            'Zip Code': '330331303'
        }, 'SW 284 ST & US 1, Homestead, FL 33033')
    )
    @unpack
    def test_parse_default_mapping(self, input, expected):
        parser = AddressRecordParser()
        result = parser.parse(input)
        self.assertEqual(expected, str(result))