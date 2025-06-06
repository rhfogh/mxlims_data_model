# generated by datamodel-codegen:
#   filename:  core/Dataset.json

from __future__ import annotations

from typing import Optional
from uuid import UUID

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field


class Dataset(BaseModel):
    """
    Base class for MXLIMS Datasets
    """

    source_id: Optional[UUID] = Field(
        None, alias="sourceId", description="uuid for Dataset source", title="SourceId"
    )
    derived_from_id: Optional[UUID] = Field(
        None,
        alias="derivedFromId",
        description="uuid for Dataset from which Dataset is derived",
        title="DerivedFromId",
    )
    logistical_sample_id: Optional[UUID] = Field(
        None,
        alias="logisticalSampleId",
        description="uuid for LogisticalSample related to Dataset",
        title="LogisticalSampleId",
    )
