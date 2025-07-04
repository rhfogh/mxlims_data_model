# generated by mxlims/impl/generate_code.py
#  filename mxlims_messages.py

""" MXLIMS message classes to use: Containing implementation + generated pydantic
"""
    
from __future__ import annotations

from typing import Any, Dict, Optional

from mxlims.impl.MxlimsBase import BaseMessage, BaseModel

from pydantic import ConfigDict, Field


from .datatypes.DatasetStub import DatasetStub
from .datatypes.JobStub import JobStub
from .datatypes.LogisticalSampleStub import LogisticalSampleStub
from .datatypes.PreparedSampleStub import PreparedSampleStub
from .objects.CollectionSweep import CollectionSweep
from .objects.Crystal import Crystal
from .objects.Dewar import Dewar
from .objects.DropRegion import DropRegion
from .objects.Macromolecule import Macromolecule
from .objects.MacromoleculeSample import MacromoleculeSample
from .objects.Medium import Medium
from .objects.MultiPin import MultiPin
from .objects.MxExperiment import MxExperiment
from .objects.MxProcessing import MxProcessing
from .objects.Pin import Pin
from .objects.PinPosition import PinPosition
from .objects.Plate import Plate
from .objects.PlateWell import PlateWell
from .objects.Puck import Puck
from .objects.ReflectionSet import ReflectionSet
from .objects.Shipment import Shipment
from .objects.WellDrop import WellDrop

class MxlimsMessageStrict(BaseModel, BaseMessage):
    """
    Message containing all possible objects, by type
    """

    collection_sweep: Optional[Dict[str, CollectionSweep]] = Field(
        default_factory=dict,
        alias="CollectionSweep",
        description="idString:object dictionary of CollectionSweeps.",
        title="CollectionSweeps",
    )
    crystal: Optional[Dict[str, Crystal]] = Field(
        default_factory=dict,
        alias="Crystal",
        description="idString:object dictionary of Crystals.",
        title="Crystals",
    )
    dewar: Optional[Dict[str, Dewar]] = Field(
        default_factory=dict,
        alias="Dewar",
        description="idString:object dictionary of Dewars.",
        title="Dewars",
    )
    drop_region: Optional[Dict[str, DropRegion]] = Field(
        default_factory=dict,
        alias="DropRegion",
        description="idString:object dictionary of DropRegions.",
        title="DropRegions",
    )
    macromolecule: Optional[Dict[str, Macromolecule]] = Field(
        default_factory=dict,
        alias="Macromolecule",
        description="idString:object dictionary of Macromolecule (reference sample) objects.",
        title="Macromolecule",
    )
    macromolecule_sample: Optional[Dict[str, MacromoleculeSample]] = Field(
        default_factory=dict,
        alias="MacromoleculeSample",
        description="idString:object dictionary of Macromolecule-containing sample objects.",
        title="MacromoleculeSample",
    )
    medium: Optional[Dict[str, Medium]] = Field(
        default_factory=dict,
        alias="Medium",
        description="idString:object dictionary of Medium (sample) objects.",
        title="Media",
    )
    mx_experiment: Optional[Dict[str, MxExperiment]] = Field(
        default_factory=dict,
        alias="MxExperiment",
        description="idString:object dictionary of MxExperiments.",
        title="MxExperiments",
    )
    mx_processing: Optional[Dict[str, MxProcessing]] = Field(
        default_factory=dict,
        alias="MxProcessing",
        description="idString:object dictionary of MxProcessings.",
        title="MxProcessings",
    )
    multi_pin: Optional[Dict[str, MultiPin]] = Field(
        default_factory=dict,
        alias="MultiPin",
        description="idString:object dictionary of MultiPins.",
        title="MultiPins",
    )
    pin: Optional[Dict[str, Pin]] = Field(
        default_factory=dict,
        alias="Pin",
        description="idString:object dictionary of Pins.",
        title="Pins",
    )
    pin_position: Optional[Dict[str, PinPosition]] = Field(
        default_factory=dict,
        alias="PinPosition",
        description="idString:object dictionary of PinPositions.",
        title="PinPositions",
    )
    plate: Optional[Dict[str, Plate]] = Field(
        default_factory=dict,
        alias="Plate",
        description="idString:object dictionary of Plates.",
        title="Plates",
    )
    plate_well: Optional[Dict[str, PlateWell]] = Field(
        default_factory=dict,
        alias="PlateWell",
        description="idString:object dictionary of PlateWells.",
        title="PlateWells",
    )
    puck: Optional[Dict[str, Puck]] = Field(
        default_factory=dict,
        alias="Puck",
        description="idString:object dictionary of Pucks.",
        title="Pucks",
    )
    reflection_set: Optional[Dict[str, ReflectionSet]] = Field(
        default_factory=dict,
        alias="ReflectionSet",
        description="idString:object dictionary of ReflectionSets.",
        title="ReflectionSets",
    )
    shipment: Optional[Dict[str, Shipment]] = Field(
        default_factory=dict,
        alias="Shipment",
        description="idString:object dictionary of Shipments.",
        title="Shipments",
    )
    well_drop: Optional[Dict[str, WellDrop]] = Field(
        default_factory=dict,
        alias="WellDrop",
        description="idString:object dictionary of WellDrops.",
        title="WellDrops",
    )


class MxlimsMessage(MxlimsMessageStrict, BaseMessage):
    """
    Message containing all possible objects, by type
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    dataset: Optional[Dict[str, DatasetStub]] = Field(
        default_factory=dict,
        alias="Dataset",
        description="idString:object dictionary of Dataset stubs.",
        title="Datasets",
    )
    job: Optional[Dict[str, JobStub]] = Field(
        default_factory=dict,
        alias="Job",
        description="idString:object dictionary of Job stubs.",
        title="Jobs",
    )
    logistical_sample: Optional[Dict[str, LogisticalSampleStub]] = Field(
        default_factory=dict,
        alias="LogisticalSample",
        description="idString:object dictionary of LogisticalSample stubs.",
        title="LogisticalSamples",
    )
    prepared_sample: Optional[Dict[str, PreparedSampleStub]] = Field(
        default_factory=dict,
        alias="PreparedSample",
        description="idString:object dictionary of PreparedSample stubs.",
        title="PreparedSamples",
    )


class ShipmentMessage(MxlimsMessageStrict, BaseMessage):
    """
    Message containing a shipment of either frozen crystals or crystallization plates
    """

    shipment: Any = Field(..., alias="Shipment")
    plate: Optional[Any] = Field(default_factory=dict, alias="Plate")
    plate_well: Optional[Any] = Field(default_factory=dict, alias="PlateWell")
    well_drop: Optional[Any] = Field(default_factory=dict, alias="WellDrop")
    drop_region: Optional[Any] = Field(default_factory=dict, alias="DropRegion")
    dewar: Optional[Any] = Field(default_factory=dict, alias="Dewar")
    puck: Optional[Any] = Field(default_factory=dict, alias="Puck")
    multi_pin: Optional[Any] = Field(default_factory=dict, alias="MultiPin")
    pin: Optional[Any] = Field(default_factory=dict, alias="Pin")
    pin_position: Optional[Any] = Field(default_factory=dict, alias="PinPosition")
    macromolecule_sample: Any = Field(..., alias="MacromoleculeSample")
    macromolecule: Any = Field(..., alias="Macromolecule")
    crystal: Optional[Any] = Field(default_factory=dict, alias="Crystal")
