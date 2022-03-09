# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from ddt import ddt, data, unpack

from rcoords.models import Coordinate
from rcoords.parsers import PtvRespParser

# TODO cover failure cases
@ddt
class test_PvtRespParser(unittest.TestCase):

    @data(
        ('{"locations":[{"referencePosition":{"latitude":47.672508239746094,"longitude":-122.12815856933594},"quality":{"totalScore":90}}]}', [Coordinate(47.672508239746094, -122.12815856933594)]),
        ('{"locations":[{"referencePosition":{"latitude":0,"longitude":0},"quality":{"totalScore":1}},{"referencePosition":{"latitude":48.672508239746094,"longitude":-121.12815856933594},"quality":{"totalScore":89}}]}', [Coordinate(48.672508239746094, -121.12815856933594),Coordinate(0, 0)])
    )
    @unpack
    def test_parse(self, input, expected):
        parser = PtvRespParser()
        result = parser.parse(input)
        self.assertEqual(expected, result)
