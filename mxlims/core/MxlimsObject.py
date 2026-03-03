"""Base class for all MxlimsObjects, combining implementation and data"""

from __future__ import annotations
from typing import Any
from mxlims.impl.MxlimsImplementation import MxlimsImplementation

class MxlimsObject(MxlimsImplementation):
    """MXLIMS pydantic model top level superclass
    """
    def __init__(self, **data: Any) -> None:
        MxlimsImplementation.__init__(self, **data)