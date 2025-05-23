# generated by datamodel-codegen:
#   filename:  datatypes/Point.json

from __future__ import annotations

from typing import Literal

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import ConfigDict, Field


class Point(BaseModel):
    """
    A point marked on an image or in absolute plate space.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    region_type: Literal["point"] = Field(
        "point", alias="regionType", description="Type of region", title="Region type"
    )
    x: float = Field(..., description="The X co-ordinate of the point.")
    y: float = Field(..., description="The Y co-ordinate of the point.")
