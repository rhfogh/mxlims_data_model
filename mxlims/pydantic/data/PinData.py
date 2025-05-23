# generated by datamodel-codegen:
#   filename:  data/PinData.json

from __future__ import annotations

from typing import Literal, Optional

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field, conint


class PinData(BaseModel):
    """
    A Pin mounted on a puck with one or more slots for crystals.
    """

    mxlims_type: Literal["Pin"] = Field(
        "Pin",
        alias="mxlimsType",
        description="The type of MXLIMS object.",
        title="MxlimsType",
    )
    barcode: Optional[str] = Field(None, description="The Pin barcode or RFID code")
    number_positions: Optional[conint(ge=1)] = Field(
        1,
        alias="numberPositions",
        description="The number of positions available in the Pin.",
    )
    position_in_puck: conint(ge=1) = Field(
        ...,
        alias="positionInPuck",
        description="The puck position occupied by the pin. This should be validated against the puck's numberPositions property.",
        examples=[16],
    )
