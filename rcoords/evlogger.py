# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=useless-super-delegation
# pylint: disable=keyword-arg-before-vararg

from enum import Enum
import logging
import traceback

from typing import Any, Optional, Tuple

from structlog import BoundLoggerBase
from structlog.types import ExcInfo
from structlog._log_levels import _LEVEL_TO_NAME

class BoundLoggerEvents(BoundLoggerBase): # pylint: disable=too-many-public-methods
    '''
    Bound logger that unpacks event dataclasses before passing
    to standard library logger.

    See structlog.stdlib.BoundLogger for details, this class is almost
    an identical copy. Given that this implementation is almost identical,
    we only test the changed area and do not aim for 100% coverage,
    nor will be rigorous about linting. It will make porting
    changes to the structlog library easier to retrofit here.

    '''

    _logger: logging.Logger

    def bind(self, **new_values: Any) -> "BoundLoggerEvents":
        return super().bind(**new_values)  # type: ignore

    def unbind(self, *keys: str) -> "BoundLoggerEvents":
        return super().unbind(*keys)  # type: ignore

    def try_unbind(self, *keys: str) -> "BoundLoggerEvents":
        return super().try_unbind(*keys)  # type: ignore

    def new(self, **new_values: Any) -> "BoundLoggerEvents":
        return super().new(**new_values)  # type: ignore

    def debug(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger("debug", event, *args, **kw)

    def info(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger("info", event, *args, **kw)

    def warning(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger("warning", event, *args, **kw)

    warn = warning

    def error(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger("error", event, *args, **kw)

    def critical(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger("critical", event, *args, **kw)

    def exception(self, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        kw.setdefault("exc_info", True)

        return self.error(event, *args, **kw)

    def log(self, level: int, event: Optional[str] = None, *args: Any, **kw: Any) -> Any:
        return self._proxy_to_logger(_LEVEL_TO_NAME[level], event, *args, **kw)

    fatal = critical

    def _proxy_to_logger(
        self,
        method_name: str,
        event: Optional[str] = None,
        *event_args: str,
        **event_kw: Any,
    ) -> Any:
        if event_args:
            event_kw["positional_args"] = event_args

        (event_name, event_fields) = self.__class__.unpack_event(event)
        return super()._proxy_to_logger(
            method_name,
            event=event_name,
            **event_kw | event_fields)

    @classmethod
    def unpack_event(cls, event):
        '''
        Unpack all fields of an event object
        '''
        event_fields = {}
        for key, value in event.__dict__.items():
            if type(value) in (int, str, bool):
                event_fields[key] = value
            elif isinstance(value, Enum):
                event_fields[key] = value.value
                event_fields[f'{key}_name'] = value.name
            elif isinstance(value, BaseException):
                event_fields[key] = ''.join(traceback.format_exception(type(value), value=value, tb=value.__traceback__))
            else:
                event_fields[key] = str(value)
        return event.__class__.__name__, event_fields

    #
    # Pass-through attributes and methods to mimic the stdlib's logger
    # interface.
    #

    @property
    def name(self) -> str:
        return self._logger.name

    @property
    def level(self) -> int:
        return self._logger.level

    @property
    def parent(self) -> Any:
        return self._logger.parent

    @property
    def propagate(self) -> bool:
        return self._logger.propagate

    @property
    def handlers(self) -> Any:
        return self._logger.handlers

    @property
    def disabled(self) -> int:
        return self._logger.disabled

    def setLevel(self, level: int) -> None:
        self._logger.setLevel(level)

    def findCaller(
        self, stack_info: bool = False
    ) -> Tuple[str, int, str, Optional[str]]:
        return self._logger.findCaller(stack_info=stack_info)

    def makeRecord( # pylint: disable=too-many-arguments
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: str,
        args: Tuple[Any, ...],
        exc_info: ExcInfo,
        func: Optional[str] = None,
        extra: Any = None,
    ) -> logging.LogRecord:
        return self._logger.makeRecord(
            name, level, fn, lno, msg, args, exc_info, func=func, extra=extra
        )

    def handle(self, record: logging.LogRecord) -> None:
        self._logger.handle(record)

    def addHandler(self, hdlr: logging.Handler) -> None:
        self._logger.addHandler(hdlr)

    def removeHandler(self, hdlr: logging.Handler) -> None:
        self._logger.removeHandler(hdlr)

    def hasHandlers(self) -> bool:
        return self._logger.hasHandlers()

    def callHandlers(self, record: logging.LogRecord) -> None:
        self._logger.callHandlers(record)  # type: ignore

    def getEffectiveLevel(self) -> int:
        return self._logger.getEffectiveLevel()

    def isEnabledFor(self, level: int) -> bool:
        return self._logger.isEnabledFor(level)

    def getChild(self, suffix: str) -> logging.Logger:
        return self._logger.getChild(suffix)
