"""Base class for all MxlimsObjects, combining implementation and data"""

from __future__ import annotations
from typing import Any
from mxlims.impl.MxlimsBase import MxlimsImplementation, BaseModel

class MxlimsObject(BaseModel, MxlimsImplementation):
    """MXLIMS pydantic model top level superclass
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        MxlimsImplementation.__init__(self)