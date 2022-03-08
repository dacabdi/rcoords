# pylint: disable=duplicate-code
''' Test with JUnit results '''

import unittest
import xmlrunner

def main():
    ''' Entry point for results generator '''
    with open('unittest-results.xml', '+wb') as output:
        unittest.main(argv=['test', 'discover'], module=None,
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False,
            verbosity=2, tb_locals=True)

main()
