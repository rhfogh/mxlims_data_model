# generated by datamodel-codegen:
#   filename:  datatypes/DatasetStub.json

from __future__ import annotations

from typing import Literal
from uuid import UUID

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import ConfigDict, Field


class DatasetStub(BaseModel):
    """
    Uuid container, used for Uuid-only links to Datasets in messages
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    mxlims_base_type: Literal["Dataset"] = Field(
        "Dataset",
        alias="mxlimsBaseType",
        description="The type of the MXLIMS core object referred to",
        title="MxlimsBaseType",
    )
    uuid: UUID = Field(
        ...,
        description="Permanent unique identifier string of object referred to",
        title="Uuid",
    )
