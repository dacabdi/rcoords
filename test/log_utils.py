# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import logging
import structlog

from rcoords.evlogger import BoundLoggerEvents

def setup_test_event_logger():
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=BoundLoggerEvents,
        cache_logger_on_first_use=False)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
