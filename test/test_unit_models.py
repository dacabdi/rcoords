# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import os
import unittest
from io import StringIO

from rcoords.models import Coordinate, Store

class test_Store(unittest.TestCase):

    def test_from_file(self):
        self.maxDiff = None
        input = \
            "id,discrepancy,Provider1_lat,Provider1_lon,Provider2_lat,Provider2_lon,Provider3_lat,Provider3_lon\n" \
          + "1,2.8284271247461903,1.0,-1.0,2.0,-2.0,3.0,-3.0\n" \
          + "2,1.4142135623730951,None,None,2.0,-2.0,3.0,-3.0\n" \
          + "3,2.8284271247461903,1.0,-1.0,2.0,-2.0,3.0,-3.0\n" \
          + "42,2.8284271247461903,1.0,-1.0,2.0,-2.0,3.0,-3.0"
        file = StringIO(input)
        store = Store.from_file(file)

        self.assertIsNone(store.get_result('0'), msg='because there is no 0 id')
        self.assertIsNone(store.get_result('1', provider_tag='ProviderX'), msg='because there is no ProviderX')
        self.assertIsNone(store.get_result('2', provider_tag='Provider1'), msg='because that provider is marked as no result')
        self.assertEqual(Coordinate(1.0, -1.0), store.get_result('1', provider_tag='Provider1'), msg='because that is the result for Provider1 on id 1')
        self.assertEqual(input, str(store))
