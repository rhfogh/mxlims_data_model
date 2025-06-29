# generated by datamodel-codegen:
#   filename:  data/DewarData.json

from __future__ import annotations

from typing import Optional

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field

from ..datatypes.TrackingDevice import TrackingDevice


class DewarData(BaseModel):
    """
    A dewar containing pucks with mounted crystals on pins.
    """

    barcode: Optional[str] = Field(None, description="The dewar barcode or RFID code")
    tracking_device: Optional[TrackingDevice] = Field(None, alias="trackingDevice")
