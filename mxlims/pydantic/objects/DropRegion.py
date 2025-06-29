# generated by mxlims/impl/generate_code.py
#  filename DropRegion.py

# NB Literal and UUID have to be imported to avoid pydantic errors
from __future__ import annotations
from pydantic import Field
from typing import Any, Literal, Optional, Union, TYPE_CHECKING
from uuid import UUID, uuid1
from mxlims.impl.MxlimsBase import MxlimsImplementation
from ..core.LogisticalSample import LogisticalSample
from ..data.LogisticalSampleData import LogisticalSampleData
from ..data.DropRegionData import DropRegionData
if TYPE_CHECKING:
    from .CollectionSweep import CollectionSweep
    from .Crystal import Crystal
    from .MacromoleculeSample import MacromoleculeSample
    from .MxExperiment import MxExperiment
    from .MxProcessing import MxProcessing
    from .ReflectionSet import ReflectionSet
    from .WellDrop import WellDrop

class DropRegion(DropRegionData, LogisticalSampleData, LogisticalSample, MxlimsImplementation):
    """MXLIMS pydantic model class for DropRegion
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        MxlimsImplementation.__init__(self)
        
    mxlims_base_type: Literal["LogisticalSample"] = Field(
        "LogisticalSample",
        alias="mxlimsBaseType",
        description="The abstract (super)type of MXLIMS object.",
        title="MxlimsBaseType",
        exclude=True,
        frozen=True
    )
    mxlims_type: Literal["DropRegion"] = Field(
        "DropRegion",
        alias="mxlimsType",
        description="The type of MXLIMS object.",
        title="MxlimsType",
        frozen=True,
    )
    uuid: Optional[UUID] = Field(
        default_factory=uuid1,
        description="Permanent unique identifier string",
        title="Uuid",
        frozen=True
    )
    
    @property
    def container(self) -> Optional[WellDrop]:
        """getter for DropRegion.container"""
        return self._get_link_n1("LogisticalSample", "container_id")

    @container.setter
    def container(self, value: Optional[WellDrop]):
        """setter for DropRegion.container"""
        from .WellDrop import WellDrop

        if value is None or isinstance(value, WellDrop):
            self._set_link_n1("LogisticalSample", "container_id", value)
        else:
            raise ValueError("container must be of type WellDrop or None")

    @property
    def contents(self) -> list[Crystal]:
        """getter for DropRegion.contents list"""
        return self._get_link_1n("LogisticalSample", "container_id")

    @contents.setter
    def contents(self, values: list[Crystal]):
        """setter for DropRegion.contents list"""
        from .Crystal import Crystal

        for obj in values:
            if not isinstance(obj, Crystal):
                raise ValueError("%s is not of type Crystal" % obj)
        self._set_link_1n_rev("LogisticalSample", "container_id", values)

    @property
    def datasets(self) -> list[Union[CollectionSweep, ReflectionSet]]:
        """getter for DropRegion.datasets list"""
        return self._get_link_1n("Dataset", "logistical_sample_id")

    @datasets.setter
    def datasets(self, values: list[Union[CollectionSweep, ReflectionSet]]):
        """setter for DropRegion.datasets list"""
        from .ReflectionSet import ReflectionSet
        from .CollectionSweep import CollectionSweep

        for obj in values:
            if not isinstance(obj, Union[CollectionSweep, ReflectionSet]):
                raise ValueError("%s is not of type Union[CollectionSweep, ReflectionSet]" % obj)
        self._set_link_1n_rev("Dataset", "logistical_sample_id", values)

    @property
    def jobs(self) -> list[Union[MxExperiment, MxProcessing]]:
        """getter for DropRegion.jobs list"""
        return self._get_link_1n("Job", "logistical_sample_id")

    @jobs.setter
    def jobs(self, values: list[Union[MxExperiment, MxProcessing]]):
        """setter for DropRegion.jobs list"""
        from .MxExperiment import MxExperiment
        from .MxProcessing import MxProcessing

        for obj in values:
            if not isinstance(obj, Union[MxExperiment, MxProcessing]):
                raise ValueError("%s is not of type Union[MxExperiment, MxProcessing]" % obj)
        self._set_link_1n_rev("Job", "logistical_sample_id", values)

    @property
    def sample(self) -> Optional[MacromoleculeSample]:
        """getter for DropRegion.sample"""
        return self._get_link_n1("PreparedSample", "sample_id")

    @sample.setter
    def sample(self, value: Optional[MacromoleculeSample]):
        """setter for DropRegion.sample"""
        from .MacromoleculeSample import MacromoleculeSample

        if value is None or isinstance(value, MacromoleculeSample):
            self._set_link_n1("PreparedSample", "sample_id", value)
        else:
            raise ValueError("sample must be of type MacromoleculeSample or None")
