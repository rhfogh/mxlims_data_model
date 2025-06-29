# generated by datamodel-codegen:
#   filename:  data/MacromoleculeData.json

from __future__ import annotations

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field


class MacromoleculeData(BaseModel):
    """
    Sample defining the Macromolecule main component of another sample
    """

    acronym: str = Field(
        ..., description="Acronym - short synonym of macromolecule", title="Acronym"
    )
