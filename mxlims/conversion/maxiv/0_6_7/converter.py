"""Adjusting functions, part of the map-driven conversion between MXLIMS and spreadsheet format"""

from typing import TYPE_CHECKING, Any, Dict, Tuple
if TYPE_CHECKING:
    from mxlims.pydantic.core.MxlimsObject import MxlimsObject

def adjust_row(
    objs: Dict[str, MxlimsObject],
    mapping:Dict[str, list[str]],
    row: Dict[str, Any]
):
    """Adjust contents of pre-generated row in place

    Allows for changes not possible with simple mapping"""
    beamsize = row.get("beam diameter")
    if beamsize:
        row["beam diameter"] = max(beamsize)


def adjust_mxlims(
    objs: Dict[str, MxlimsObject],
    mapping:Dict[str, list[str]],
    row: Dict[str, Any]
):
    """Adjust contents of MxlimsObjects in place

    Allows for changes not possible with simple mapping"""
    pass