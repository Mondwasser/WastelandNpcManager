from typing import Protocol


class HasGroup(Protocol):
    """Protocol classes that have group attribute"""

    group: str
    """Name of the group this object belongs to"""