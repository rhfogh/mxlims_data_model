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
import datetime
import enum
from typing import Optional, Dict, List, Any,Union
from pydantic import BaseModel, Field


class JobStatus(str, enum.Enum):
    Template = "Template"
    Ready = "Ready"
    Running = "Running"
    Completed = "Completed"
    Failed = "	Failed"
    Aborted = "Aborted"


class MxlimsObject(BaseModel):
    """Basic abstract MXLIMS object, with attributes shared by all MXLIMS objects"""

    uuid: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        frozen=True,
        json_schema_extra={"description": "Permanent unique identifier string"},
    )
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Keyword-value dictionary string:Any of extensions."
            "Use is accepted but discouraged"
        },
    )
    namespace_extensions: Dict[str, BaseModel] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Keyword-value dictionary of namespaced extension. "
             "Key is an organisation identifier (e.g. 'GPhL' or 'ESRF'),"
            " value is a Pydantic model defined by this organisation.",
        },
    )


class Dataset(MxlimsObject):
    """Base class for MXLIMS Datasets"""

    source_id: Optional[str] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "String UUID for Job that created this Dataset."
                           "return link for job.results"
        },
    )
    role: Optional[str] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "Role of Dataset realtive to the source Job."
            "Intended for filtering of Datasets",
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
        json_schema_extra={
            "description": "String UUID for Logistical Sample relevant to Dataset."
        },
    )
    derived_from_id: Optional[str] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "String UUID for Dataset from which this Dataset was derived. "
            "Used for modified Datasets without a 'source' link, "
            "e.g. when removing images from a sweep before processing."
        },
    )


class Job(MxlimsObject):
    """Base class for MXLIMS Jobs - an experiment or calculation producing Datasets"""

    sample: Optional["PreparedSample"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "Prepared sample relevant to Job."
            "return link for PreparedSample.jobs"
        },
    )
    logistical_sample: Optional["LogisticalSample"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "Logistical Sample or Sample location relevant to Job."
            "Overridden by Dataset.logistical_sample; return link for Logisticalsample.jobs"
        },
    )
    templates: Union[List[Dataset], List[str]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Lisdt of Templates with parameters for output datasets "
            "– e.g. diffraction plan, processing plan, or of their String UUID",
        },
    )
    input_data: Union[List[Dataset], List[str]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "List of pre-existing Input data sets used for calculation,"
            " or of their String UUID",
        },
    )
    reference_data: Union[List[Dataset], List[str]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "List of reference data sets, e.g. reference mtz file, "
            "or of their String UUID",
        },
    )
    results: List[Dataset] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Datasets produced by Job (match Dataset.source_id",
        },
    )
    start_time: Optional[datetime.datetime] = Field(
        default=None,
        json_schema_extra={
            "description": "Actual starting time for job or calculation, ",
        },
    )
    end_time: Optional[datetime.datetime] = Field(
        default=None,
        json_schema_extra={
            "description": "Actual finishing time for job or calculation, ",
        },
    )
    job_status: Optional[JobStatus] = Field(
        default=None,
        json_schema_extra={
            "description": "Status of job - enumerated, ",
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


class LogisticalSample(MxlimsObject):
    """Base class for MXLIMS Logistical Samples

    describing Sample containers and locations
    (from Dewars and Plates to drops, pins and crystals)"""
    sample_id: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "String UUID for the sample preparation that applies "
            "to this LogisticalSample and all its contents",
        },
    )
    container: Optional["LogisticalSample"] = Field(
        default=None,
        json_schema_extra={
            "description": "The LogisticalSample containing this one",
        },
    )
    contents: List["LogisticalSample"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "LogisticalSamples contained in this one",
        },
    )


class PreparedSample(MxlimsObject):
    """Base class for MXLIMS Prepared Samples, describing sample content"""
    logistical_samples: List[LogisticalSample] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "LogisticalSamples with contents from this LogisticalSample",
        },
    )
    jobs: List[Job] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Jobs (templates, planned, initiated or completed)"
            "for this PreparedSample",
        },
    )
