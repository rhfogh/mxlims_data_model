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

class MxlimsObject(BaseModel):
    """Basic abstract MXLIMS object, with attributes shared by all MXLIMS objects"""
    mxlims_type: Literal["MxlimsObject"] = Field(
        default="MxlimsObject",
        description="The type of MXLIMS object.",
    )

    version: Literal[mxlims.version()] = Field(
        default=mxlims.version(),
        description="MXLIMS version for current model",
    )

    uuid: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        frozen=True,
        json_schema_extra={"description": "Permanent unique identifier string"},
    )
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword-value dictionary string:Any of extensions."
        "Use is accepted but discouraged",
    )
    namespace_extensions: Dict[str, BaseModel] = Field(
        default_factory=dict,
        description="Keyword-value dictionary of namespaced extension. "
        "Key is an organisation identifier (e.g. 'GPhL' or 'ESRF'),"
        " value is a Pydantic model defined by this organisation.",
    )

class MxlimsObjectRef(BaseModel):
    """Reference to MXLIMS model object, for use in JSON files."""
    mxlims_type: Literal["MxlimsObjectRef"] = Field(
        default="MxlimsObjectRef",
        description="The type of MXLIMS object.",
    )
    target_uuid: str = Field(
        frozen=True,
        description="UUID of target MXLIMS model object",
    )
    target_type: Literal["MxlimsObject"] = Field(
        default="MxlimsObject",
        description="The type of MXLIMS object linked to.",
    )


class Dataset(MxlimsObject):
    """Base class for MXLIMS Datasets"""
    mxlims_type: Literal["Dataset"] = Field(
        default="Dataset",
        description="The type of MXLIMS object.",
    )

    source_ref: Optional["JobRef"] = Field(
        default=None,
        frozen=True,
        description="Reference to Job that created this Dataset.",
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
    logistical_sample_ref: Optional["LogisticalSampleRef"] = Field(
        default=None,
        frozen=True,
        description="Reference to LogisticalSample relevant to Dataset."
    )
    derived_from_ref: Optional["DatasetRef"] = Field(
        default=None,
        frozen=True,
        description="Reference to Dataset from which this Dataset was derived. "
        "Used for modified Datasets without a 'source' link, "
        "e.g. when removing images from a sweep before processing.",
    )
    derived_dataset_refs: List["DatasetRef"] = Field(
        default_factory=list,
        description="List of references to Datasets derived from Dataset.",
    )

class DatasetRef(MxlimsObjectRef):
    """Reference to Dataset object, for use in JSON files."""
    target_type: Literal["Dataset"] = Field(
        default="Dataset",
        description="The type of MXLIMS object linked to.",
    )


class Job(MxlimsObject):
    """Base class for MXLIMS Jobs - an experiment or calculation producing Datasets"""

    mxlims_type: Literal["Job"] = Field(
        default="Job",
        description="The type of MXLIMS object.",
    )
    sample: Optional["PreparedSample"] = Field(
        default=None,
        frozen=True,
        description="Prepared sample relevant to Job.",
    )
    logistical_sample: Optional["LogisticalSample"] = Field(
        default=None,
        frozen=True,
        description="Logistical Sample (or sample location) relevant to Job.",
    )
    results: List[Dataset] = Field(
        default_factory=list,
        description="Datasets produced by Job (match Dataset.source_ref",
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

class JobRef(MxlimsObjectRef):
    """Reference to Job object, for use in JSON files."""
    target_type: Literal["Job"] = Field(
        default="Job",
        description="The type of MXLIMS object linked to.",
    )

class LogisticalSample(MxlimsObject):
    """Base class for MXLIMS Logistical Samples

    describing Sample containers and locations
    (from Dewars and Plates to drops, pins and crystals)"""

    mxlims_type: Literal["LogisticalSample"] = Field(
        default="LogisticalSample",
        description="The type of MXLIMS object."
    )
    sample_ref: Optional["PreparedSampleRef"] = Field(
        default=None,
        description="Reference to the PreparedSemple that applies "
        "to this LogisticalSample and all its contents",
    )
    container_ref: Optional["LogisticalSampleRef"] = Field(
        default=None,
        frozen=True,
        description="Reference to the LogisticalSample containing this one",
    )
    contents: List["LogisticalSample"] = Field(
        default_factory=list,
        description="LogisticalSamples contained in this one",
    )
    job_refs: List[JobRef] = Field(
        default_factory=list,
        discriminator="target_type",
        description="References to Jobs (templates, planned, initiated or completed)"
        "applied to this LogisticalSample",
    )
    dataset_refs: List[DatasetRef] = Field(
        default_factory=list,
        discriminator="target_type",
        description="References to Datasets "
        "that pertain specifically to this LogisticalSample",
    )

class LogisticalSampleRef(MxlimsObjectRef):
    """Reference to LogisticalSample object, for use in JSON files."""
    target_type: Literal["LogisticalSample"] = Field(
        default="LogisticalSample",
        description="The type of MXLIMS object linked to.",
    )

class PreparedSample(MxlimsObject):
    """Base class for MXLIMS Prepared Samples, describing sample content"""

    mxlims_type: Literal["PreparedSample"] = Field(
        default="PreparedSample",
        description="The type of MXLIMS object.",
    )
    logistical_sample_refs: List[LogisticalSampleRef] = Field(
        default_factory=list,
        description="LogisticalSamples with contents from this PreparedSample",
    )
    job_refs: List[JobRef] = Field(
        default_factory=list,
        description="References to Jobs (templates, planned, initiated or completed)"
        "for this PreparedSample",
    )

class PreparedSampleRef(MxlimsObjectRef):
    """Reference to PreparedSample object, for use in JSON files."""
    target_type: Literal["PreparedSample"] = Field(
        default="PreparedSample",
        description="The type of MXLIMS object linked to.",
    )
