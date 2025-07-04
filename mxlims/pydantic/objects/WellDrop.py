# generated by mxlims/impl/generate_code.py
#  filename WellDrop.py

# NB Literal and UUID have to be imported to avoid pydantic errors
from __future__ import annotations
from pydantic import Field
from typing import Any, Literal, Optional, Union, TYPE_CHECKING
from uuid import UUID, uuid1
from mxlims.impl.MxlimsBase import MxlimsImplementation
from ..core.LogisticalSample import LogisticalSample
from ..data.LogisticalSampleData import LogisticalSampleData
from ..data.WellDropData import WellDropData
if TYPE_CHECKING:
    from .CollectionSweep import CollectionSweep
    from .DropRegion import DropRegion
    from .MacromoleculeSample import MacromoleculeSample
    from .MxExperiment import MxExperiment
    from .MxProcessing import MxProcessing
    from .PlateWell import PlateWell
    from .ReflectionSet import ReflectionSet

class WellDrop(WellDropData, LogisticalSampleData, LogisticalSample, MxlimsImplementation):
    """MXLIMS pydantic model class for WellDrop
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
    mxlims_type: Literal["WellDrop"] = Field(
        "WellDrop",
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
    def container(self) -> Optional[PlateWell]:
        """getter for WellDrop.container"""
        return self._get_link_n1("LogisticalSample", "container_id")

    @container.setter
    def container(self, value: Optional[PlateWell]):
        """setter for WellDrop.container"""
        from .PlateWell import PlateWell

        if value is None or isinstance(value, PlateWell):
            self._set_link_n1("LogisticalSample", "container_id", value)
        else:
            raise ValueError("container must be of type PlateWell or None")

    @property
    def contents(self) -> list[DropRegion]:
        """getter for WellDrop.contents list"""
        return self._get_link_1n("LogisticalSample", "container_id")

    @contents.setter
    def contents(self, values: list[DropRegion]):
        """setter for WellDrop.contents list"""
        from .DropRegion import DropRegion

        for obj in values:
            if not isinstance(obj, DropRegion):
                raise ValueError("%s is not of type DropRegion" % obj)
        self._set_link_1n_rev("LogisticalSample", "container_id", values)

    @property
    def datasets(self) -> list[Union[CollectionSweep, ReflectionSet]]:
        """getter for WellDrop.datasets list"""
        return self._get_link_1n("Dataset", "logistical_sample_id")

    @datasets.setter
    def datasets(self, values: list[Union[CollectionSweep, ReflectionSet]]):
        """setter for WellDrop.datasets list"""
        from .ReflectionSet import ReflectionSet
        from .CollectionSweep import CollectionSweep

        for obj in values:
            if not isinstance(obj, Union[CollectionSweep, ReflectionSet]):
                raise ValueError("%s is not of type Union[CollectionSweep, ReflectionSet]" % obj)
        self._set_link_1n_rev("Dataset", "logistical_sample_id", values)

    @property
    def jobs(self) -> list[Union[MxExperiment, MxProcessing]]:
        """getter for WellDrop.jobs list"""
        return self._get_link_1n("Job", "logistical_sample_id")

    @jobs.setter
    def jobs(self, values: list[Union[MxExperiment, MxProcessing]]):
        """setter for WellDrop.jobs list"""
        from .MxExperiment import MxExperiment
        from .MxProcessing import MxProcessing

        for obj in values:
            if not isinstance(obj, Union[MxExperiment, MxProcessing]):
                raise ValueError("%s is not of type Union[MxExperiment, MxProcessing]" % obj)
        self._set_link_1n_rev("Job", "logistical_sample_id", values)

    @property
    def sample(self) -> Optional[MacromoleculeSample]:
        """getter for WellDrop.sample"""
        return self._get_link_n1("PreparedSample", "sample_id")

    @sample.setter
    def sample(self, value: Optional[MacromoleculeSample]):
        """setter for WellDrop.sample"""
        from .MacromoleculeSample import MacromoleculeSample

        if value is None or isinstance(value, MacromoleculeSample):
            self._set_link_n1("PreparedSample", "sample_id", value)
        else:
            raise ValueError("sample must be of type MacromoleculeSample or None")
