#! /usr/bin/env python
# encoding: utf-8
#
"""

License:

This file is part of the MXLIMS collaboration.

MXLIMS models and code are free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MXLIMS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with MXLIMS. If not, see <https://www.gnu.org/licenses/>.
"""

__copyright__ = """ Copyright © 2024 -  2024 MXLIMS collaboration."""
__author__ = "rhfogh"
__date__ = "17/10/2024"

import uuid
from datetime import datetime
import enum
from typing import Optional, Dict, List, Any, Union, Literal
from typing_extensions import Annotated

import mxlims
from pydantic import BaseModel, Field, PlainSerializer

# Datetime type that prints to JSON as isoformat (e.g. '2019-05-18T15:17:08.132263')
DatetimeStr = Annotated[datetime, PlainSerializer(datetime.isoformat)]

class JobStatus(str, enum.Enum):
    Template = "Template"
    Ready = "Ready"
    Running = "Running"
    Completed = "Completed"
    Failed = "	Failed"
    Aborted = "Aborted"

class MxlimsData(BaseModel):
    """Abstract superclass for Metadata"""
    mxlims_type: str = Field(
        description="The type of MXLIMS data. May be restricted to enum in subclasses",
    )
    version: str = Field(
        default=mxlims.version(),
        description="MXLIMS version for specific Metadata class",
    )
    namespace_extensions: Dict[str, BaseModel] = Field(
        default_factory=dict,
        description="Keyword-value dictionary of namespaced extension. "
        "Key is an organisation identifier (e.g. 'GPhL' or 'ESRF'),"
        " value is a Pydantic model defined by this organisation.",
    )

class MxlimsObject(BaseModel):
    """Basic abstract MXLIMS object, with attributes shared by all MXLIMS objects"""
    version: Literal[mxlims.version()] = Field(
        default=mxlims.version(),
        description="MXLIMS version for current model",
    )
    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid1()),
        frozen=True,
        json_schema_extra={"description": "Permanent unique identifier string"},
    )
    data: MxlimsData = Field(
        description="Metadata object, also defining the precise type.",
    )
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword-value dictionary string:Any of extensions."
        "Use is accepted but discouraged",
    )


class Dataset(MxlimsObject):
    """Base class for MXLIMS Datasets"""
    source_id: str = Field(
        default=None,
        frozen=True,
        description="String UUID of Job that created this Dataset.",
    )
    role: Optional[str] = Field(
        default=None,
        frozen=True,
        description="Role of Dataset realtive to the source Job."
        "Intended for filtering of Datasets",
        json_schema_extra={
            "examples": [
                "Result",
                "Intermediate",
                "Characterisation",
                "Centring",
            ],
        },
    )
    logistical_sample_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of LogisticalSample relevant to Dataset."
    )
    derived_from_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of Dataset from which this Dataset was derived. "
        "Used for modified Datasets without a 'source' link, "
        "e.g. when removing images from a sweep before processing.",
    )


class Job(MxlimsObject):
    """Base class for MXLIMS Jobs - an experiment or calculation producing Datasets"""

    sample_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of the PreparedSample that applies to this Job",
    )
    logistical_sample_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of LogisticalSample relevant to this Job."
    )
    started_from_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of the Job from which this Job was started."
    )
    start_time: Optional[DatetimeStr] = Field(
        default=None,
        description="Actual starting time for job or calculation, ",
    )
    end_time: Optional[DatetimeStr] = Field(
        default=None,
        description="Actual finishing time for job or calculation, ",
    )
    job_status: Optional[JobStatus] = Field(
        default=None,
        description="Status of job - enumerated, ",
        json_schema_extra={
            "examples": [
                JobStatus.Template.value,
                JobStatus.Ready.value,
                JobStatus.Running.value,
                JobStatus.Completed.value,
                JobStatus.Failed.value,
                JobStatus.Aborted.value,
            ],
        },
    )
    input_data_ids: List[str] = Field(
        default_factory=list,
        description="String UUID of input Datasets for this Job."
    )
    reference_data_ids: List[str] = Field(
        default_factory=list,
        description="String UUID of reference Datasets for this Job."
    )
    template_data_ids: List[str] = Field(
        default_factory=list,
        description="String UUID of template Datasets for this Job."
    )
    subjobs: List[Job] = Field(
        default_factory=list,
        description="List of Jobs started from this job."
        "NB the started_from_id of the jobs must point to this Job."
        "This field allows attached jobs to be contained directly in the JSON file"
        "and allows for constraining job types in subtypes"
    )
    results: List[Dataset] = Field(
        default_factory=list,
        description="List of Datasets created from this job."
        "NB the source_id of the datasets must point to this Job."
        "This field allows result Datasets to be contained directly in the JSON file"
        "and allows for constraining Dataset types in subtypes"
    )
    template_data: List[Dataset] = Field(
        default_factory=list,
        description="List of Template Datasets used for this job."
        "NB the id of the datasets must match the IDs in template_data_ids."
        "This field allows template Datasets to be contained directly in the JSON file"
        "and allows for constraining Dataset types in subtypes."
        "NB Note that two different specifications of a dataset cannot have the same ID"
    )

class LogisticalSample(MxlimsObject):
    """Base class for MXLIMS Logistical Samples

    describing Sample containers and locations
    (from Dewars and Plates to drops, pins and crystals)"""

    sample_id: Optional[str] = Field(
        default=None,
        description="String UUID of the PreparedSemple that applies "
        "to this LogisticalSample and all its contents",
    )
    container_id: Optional[str] = Field(
        default=None,
        frozen=True,
        description="String UUID of the LogisticalSample containing this one",
    )
    contents: List[LogisticalSample] = Field(
        default_factory=list,
        description="List of directly contained LogisticalSamples."
        "NB the container_id of the contents must point to this LogisticalSample."
        "This field allows contents to be contained directly in the JSON file"
        "and allows for constraining content types in subtypes"
        "(E.g. Pucks can only contain contain Pins"
    )
    jobs: List[Job] = Field(
        default_factory=list,
        description="List of directly attached Jobs."
        "NB the logistical_sample_id of the jobs must point to this LogisticalSample."
        "This field allows attached jobs to be contained directly in the JSON file"
        "and allows for constraining job types in subtypes"
    )

class PreparedSample(MxlimsObject):
    """Base class for MXLIMS Prepared Samples, describing sample content"""
    pass

class MxlimsMessage(BaseModel):
    """Generic MXLIMS message.

    Links between objects are defined by the IDs they contain
    and must be dereferenced appropraitely by the reding application.
    The types and numbers of allowed contents can be restricted in subtypes of message.
    """
    samples: List[PreparedSample] = Field(
        default_factory=list,
        description="List of directly contained PreparedSamples."
    )
    logistical_samples: List[LogisticalSample] = Field(
        default_factory=list,
        description="List of directly contained LogisticalSamples."
    )
    jobs: List[Job] = Field(
        default_factory=list,
        description="List of directly contained Jobs."
    )
    samples: List[Dataset] = Field(
        default_factory=list,
        description="List of directly contained Datasets."
    )
