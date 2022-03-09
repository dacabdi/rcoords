''' Generic events '''

from dataclasses import dataclass

@dataclass(order=True)
class AppEvent:
    ''' Generic event schema, used for common schema non-specific logging '''
    message: str
    schema_ver: int = 1
