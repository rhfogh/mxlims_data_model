# generated by datamodel-codegen:
#   filename:  data/DropRegionData.json

from __future__ import annotations

from typing import Union

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field

from ..datatypes.ImageRegion import ImageRegion
from ..datatypes.PlateRegion import PlateRegion


class DropRegionData(BaseModel):
    """
    A region in a well drop where crystals may be found
    """

    region: Union[ImageRegion, PlateRegion] = Field(
        ...,
        description="The region data (either ImageRegion or PlateRegion).",
        title="Region",
    )
