'''rcoords execution module'''

import logging
import logging.config
import structlog
import asyncio
import sys
import yaml
import os

from .config import setup_configparser
from .evlogger import BoundLoggerEvents
from .events.app_event import AppEvent
from .rcoords import RCoords

logger = structlog.get_logger('rcoords')

async def main_async():
    '''
    rcoords entry point
    '''

    # setup and read configuration
    parser = setup_configparser()
    config = parser.parse() # type: ignore
    parser.print_values()

    # setup loggers
    setup_logging(config.logconf)
    logger.debug(AppEvent(f"Configuration loaded: '{str(vars(config))}'"))
    logger.debug(AppEvent(f"Current working directory: '{str(os.getcwd())}'"))

    return await RCoords(config).run()

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

main()