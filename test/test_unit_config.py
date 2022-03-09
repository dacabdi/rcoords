# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

# TODO add tests for overrides
#      and missing required parameters

import unittest
from rcoords.config import setup_configparser

class test_Config(unittest.TestCase):

    def test_config_required_and_defaults(self):
        parser = setup_configparser()
        config = parser.parse('--csv somefile.csv')
        # required
        self.assertEqual(config.csv, 'somefile.csv')
        # defaults
        self.assertEqual(config.logconf, 'logconf.yml')

    def test_config_cli_overrides_long_version(self):
        parser = setup_configparser()
        config = parser.parse(' '.join([
            '--csv somefile.csv',
            '--logconf configlog.yml',
            ]), config_file_contents='')
        self.assertEqual(config.csv, 'somefile.csv')
        self.assertEqual(config.logconf, 'configlog.yml')
