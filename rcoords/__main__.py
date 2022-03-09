'''rcoords execution module'''

import logging
import logging.config
import structlog
import asyncio
import sys
import yaml
import os
import aiofiles
import httpx
import pprint

from dataclasses import field
from aiocsv import AsyncDictReader

from .config import setup_configparser
from .evlogger import BoundLoggerEvents
from .events import AppEvent
from .client import BingClient, GoogleClient, PtvClient
from .providers import GenericProvider
from .parsers import AddressRecordParser, BingRespParser, GoogleRespParser, PlainReqParser, PtvRespParser

logger = structlog.get_logger('rcoords')

async def main_async():
    '''rcoords entry point'''

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse() # type: ignore
    parser.print_values()

    # setup loggers
    setup_logging(config.logconf)
    logger.debug(AppEvent(f"Configuration loaded: '{str(vars(config))}'"))
    logger.debug(AppEvent(f"Current working directory: '{str(os.getcwd())}'"))

    printer = pprint.PrettyPrinter(indent=4, sort_dicts=True, compact=False)
    results = {}
    address_parser = AddressRecordParser() # using default mappings
    async with httpx.AsyncClient() as http_client, aiofiles.open(config.csv, mode='r', encoding='utf-8') as csv:
        providers = create_providers(config, http_client)
        async for row in AsyncDictReader(csv, delimiter=','):
            id = row['ID']
            address = str(address_parser.parse(row))
            logger.info(AppEvent(f"Resolving address: '{address}', normalized from '{row}'"))
            locations = {}
            coords = []
            for provider in providers:
                tag = provider.tag
                try:
                    prov_results = await provider.query(address)
                    locations[tag] = [] if len(prov_results) is 0 else prov_results[0]
                    coords.append(locations[tag]) # TODO ugh, improve this
                except Exception as e:
                    logger.warn(AppEvent(f"Provider '{tag}' failed to resolve '{address}'"))
                logger.info(AppEvent(f"'{tag}' reported: '{locations[tag]}'"))
            results[id] = {'id': id}
            results[id]['locations'] = locations
            results[id]['max_distance'] = top_distance(coords)
    printer.pprint(results)

    return 0

def main():
    ''' Entry point and async main scheduler '''
    loop = asyncio.get_event_loop()
    exit_code = loop.run_until_complete(main_async())
    sys.exit(exit_code)

def setup_logging(config_path):
    ''' Setup logging configuration '''

    timestamper = structlog.processors.TimeStamper(fmt='iso')
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    # configure logging
    with open(config_path, 'rt') as config_file:
        logger_config = yaml.safe_load(config_file.read())
        # add structlog formatters
        logger_config['formatters'] = {
            'plain': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(colors=False, pad_event=0),
                'foreign_pre_chain': pre_chain,
            },
            'colored': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(colors=True, pad_event=0),
                'foreign_pre_chain': pre_chain,
            },
            'json': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.processors.JSONRenderer(indent=1, sort_keys=True),
                'foreign_pre_chain': pre_chain,
            }
        }
        create_log_dirs(logger_config)
        logging.config.dictConfig(logger_config)

    # configure structlog
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=BoundLoggerEvents,
        cache_logger_on_first_use=True)

def create_log_dirs(logger_config):
    ''' Check logger configuration for filenames and create subdirs '''
    for handler in logger_config['handlers']:
        handler_dict = logger_config['handlers'][handler]
        if 'filename' in handler_dict:
            dirpath = os.path.dirname(handler_dict['filename'])
            os.makedirs(dirpath, exist_ok=True)

def create_providers(config, http_client):
    providers = []

    if config.use_ptv:
        ptv_client = PtvClient(http_client, apikey=config.ptv_apikey)
        ptv_req_parser = PlainReqParser(field_name='searchText', common={'countryFilter':'US'})
        ptv_res_parser = PtvRespParser()
        ptv_provider = GenericProvider(ptv_client, ptv_req_parser, ptv_res_parser, tag='PTV')
        providers.append(ptv_provider)

    if config.use_google:
        gclient = GoogleClient(http_client, apikey=config.google_apikey)
        gclient_req_parser = PlainReqParser(field_name='address')
        gclient_res_parser = GoogleRespParser()
        gprovider = GenericProvider(gclient, gclient_req_parser, gclient_res_parser, tag='Google')
        providers.append(gprovider)

    if config.use_bing:
        bing_client = BingClient(http_client, apikey=config.bing_apikey)
        bing_req_parser = PlainReqParser(field_name='q')
        bing_res_parser = BingRespParser()
        bing_provider = GenericProvider(bing_client, bing_req_parser, bing_res_parser, tag='Bing')
        providers.append(bing_provider)

    return providers

def top_distance(coords):
    distances = []
    for c1 in coords:
        for c2 in coords:
            distances.append(c1.distance(c2))
    distances = sorted(distances, reverse=True)
    return distances[0] if len(distances) else [0]

main()