'''
rcoords program module facade
'''

import asyncio
import signal
import sys
import httpx
import structlog
import aiofiles
import shutil

from datetime import datetime
from aiocsv import AsyncDictReader
from os.path import exists

from .models import Store
from .events import AppEvent
from .client import BingClient, GoogleClient, PtvClient
from .providers import GenericProvider
from .parsers import AddressRecordParser, BingRespParser, GoogleRespParser, PlainReqParser, PtvRespParser

logger = structlog.get_logger('rcoords')

class RCoords:
    '''
    rcoords program class
    '''

    def __init__(self, config):
        self._config = config
        self._http_client = httpx.AsyncClient()
        self._providers = self._create_providers()
        self._store = self._create_store()
        self._address_parser = AddressRecordParser() # using default mappings
        self._setup_signals()
        self._counter = 0

    async def run(self):
        '''
        resolve one address at a time over all providers
        every n addresses, wait a configured delay
        '''
        async with aiofiles.open(self._config.csv, mode='r', encoding='utf-8') as csv:
            async for entry in AsyncDictReader(csv, delimiter=','):
                # handle process signals (e.g. ctrl+c == SIGTERM in *nix)
                if self._signal:
                    signal_name = str(signal.Signals(self._signal)).removeprefix('Signals.') # pylint: disable=no-member
                    logger.warning(AppEvent(f'Received signal \'{signal_name}\', exiting now'))
                    self._save_work()
                    return 1

                await self._process_entry(entry)

                # cooldown and save work
                if self._counter != 0 and self._counter % self._config.burst_size == 0:
                    logger.info(AppEvent(f'Cooling down for {self._config.cooldown_ms} milliseconds'))
                    await asyncio.sleep(self._config.cooldown_ms / 1000) # sleep expects seconds
                    self._save_work()

        logger.info(AppEvent(f'Processed {self._counter} new entries'))
        self._save_work()
        return 0

    def _save_work(self):
        logger.info(AppEvent(f'Saving work so far!'))
        with open(self._config.store, mode='w') as storefile:
            storefile.write(str(self._store))

    async def _process_entry(self, entry):
        accounted = False
        id = entry['id']
        address = str(self._address_parser.parse(entry))

        logger.info(AppEvent(f"Resolving address: '{address}', normalized from '{entry}'"))

        for provider in self._providers:
            tag = provider.tag
            result = None

            # check already existing result
            previous = self._store.get_result(id, tag)
            if not previous:
                accounted = True
                try:
                    result = await provider.query(address)
                    result = None if len(result) == 0 else result[0]
                except Exception as e:
                    logger.warn(AppEvent(f"Provider '{tag}' failed to resolve '{address}' with exception {e}"))
                logger.info(AppEvent(f"'{tag}' reported: '{result}'"))
                self._store.set_result(id, tag, result)
            else:
                logger.info(AppEvent(f"Noop, id '{id}' was already resolved for provider '{tag}'"))

        if accounted:
            self._counter += 1

    def _create_providers(self):
        '''
        creates the location providers based on configuration
        switches that enable and disable each particular provider
        '''
        providers = []

        if self._config.use_ptv:
            ptv_client = PtvClient(self._http_client, apikey=self._config.ptv_apikey)
            ptv_req_parser = PlainReqParser(field_name='searchText', common={'countryFilter':'US'})
            ptv_res_parser = PtvRespParser()
            ptv_provider = GenericProvider(ptv_client, ptv_req_parser, ptv_res_parser, tag='PTV')
            providers.append(ptv_provider)

        if self._config.use_google:
            gclient = GoogleClient(self._http_client, apikey=self._config.google_apikey)
            gclient_req_parser = PlainReqParser(field_name='address')
            gclient_res_parser = GoogleRespParser()
            gprovider = GenericProvider(gclient, gclient_req_parser, gclient_res_parser, tag='Google')
            providers.append(gprovider)

        if self._config.use_bing:
            bing_client = BingClient(self._http_client, apikey=self._config.bing_apikey)
            bing_req_parser = PlainReqParser(field_name='q')
            bing_res_parser = BingRespParser()
            bing_provider = GenericProvider(bing_client, bing_req_parser, bing_res_parser, tag='Bing')
            providers.append(bing_provider)

        return providers

    def _create_store(self):
        '''
        creates a backing store to process the data
        if the '--preload' switch is set in the configuration
        the store is preloaded with the output csv contents
        to avoid duplicating work on already resolved addresses.
        this puts forth a more idempotent behavior and reduces the
        massive hits on the providers apis for repeated work
        '''
        path = self._config.store

        if exists(path):
            ts = datetime.now()
            shutil.copyfile(self._config.store, self._config.store + '.' + ts.strftime('%Y-%m-%dT%H-%M-%S.%f%z'))

            if self._config.preload:
                logger.info(AppEvent(f"Preloading results store from '{path}'"))
                with open(path, mode='r') as store_file:
                    return Store.from_file(store_file)

        return Store()

    def _setup_signals(self):
        '''
        Subscribe to OS process signals
        '''
        self._signal = None
        self._signal_frame = None
        signal.signal(signal.SIGINT, self.signal_handler)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler) # pylint: disable=no-member
        signal.signal(signal.SIGTERM, self.signal_handler)

    # pylint: disable=attribute-defined-outside-init
    def signal_handler(self, sig, frame):
        '''
        handle signals
        '''
        # pylint: disable=line-too-long
        # NOTE do not add non-reentrant functions to this
        #      signal handler; keep it simple, stupid (KISS)
        #      https://stackoverflow.com/questions/4604634/which-functions-are-re-entrant-in-python-for-signal-library-processing
        # pylint: enable=line-too-long
        self._signal = sig
        self._signal_frame = frame
