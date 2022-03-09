'''Configuration parser and provider'''

import configargparse

def setup_configparser() -> configargparse.ArgumentParser:
    '''Sets up the configuration parser, provides command usage, etc.'''
    parser = configargparse.Parser(
        auto_env_var_prefix='RCOORDS_',
        add_config_file_help=False,)
    parser.add('--config', metavar='FILE', default='rcoords.conf', dest='config',
        is_config_file=True, env_var='RCOORDS_CONFIG', help='config file path')
    # input
    parser.add('--csv', dest='csv', type=str, required=True,
        help='input csv file to resolve locations')
    # providers
    parser.add('--google-apikey', dest='google_apikey', type=str,
        help='google api key')
    parser.add('--ptv-apikey', dest='ptv_apikey', type=str,
        help='ptv api key')
    parser.add('--bing-apikey', dest='bing_apikey', type=str,
        help='bing api key')
    parser.add('--use-google', dest='use_google', action='store_true',
        help='use google maps provider')
    parser.add('--use-ptv', dest='use_ptv', action='store_true',
        help='use ptv maps provider')
    parser.add('--use-bing', dest='use_bing', action='store_true',
        help='use bing maps provider')
    # logs
    parser.add('--logconf', default='logconf.yml', dest='logconf',
        type=str, help='yml file with the logger configuration')
    return parser
