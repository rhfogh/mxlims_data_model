# generated by mxlims/impl/generate_code.py
#  filename Macromolecule.py

# NB Literal and UUID have to be imported to avoid pydantic errors
from __future__ import annotations
from typing import Any, Literal, Optional, Union, TYPE_CHECKING
from uuid import UUID
from mxlims.impl.MxlimsBase import MxlimsImplementation
from ..core.PreparedSample import PreparedSample
from ..data.PreparedSampleData import PreparedSampleData
from ..data.MacromoleculeData import MacromoleculeData
if TYPE_CHECKING:
    from .MacromoleculeSample import MacromoleculeSample

class Macromolecule(MacromoleculeData, PreparedSampleData, PreparedSample, MxlimsImplementation):
    """MXLIMS pydantic model class for Macromolecule
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        MxlimsImplementation.__init__(self)
    
    @property
    def main_samples(self) -> list[MacromoleculeSample]:
        """getter for Macromolecule.main_samples list"""
        return self._get_link_1n("PreparedSample", "main_component_id")

    @main_samples.setter
    def main_samples(self, values: list[MacromoleculeSample]):
        """setter for Macromolecule.main_samples list"""
        from .MacromoleculeSample import MacromoleculeSample

        for obj in values:
            if not isinstance(obj, MacromoleculeSample):
                raise ValueError("%s is not of type MacromoleculeSample" % obj)
        self._set_link_1n_rev("PreparedSample", "main_component_id", values)
