"""Adjusting functions, part of the map-driven conversion between MXLIMS and spreadsheet format"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from mxlims.core.MxlimsObject import MxlimsObject

def adjust_row(
    objs: Dict[str, MxlimsObject],
    mapping:Dict[str, list[str]],
    row: Dict[str, Any]
):
    """Adjust contents of pre-generated row in place

    Allows for changes not possible with simple mapping"""
    collection_sweep = objs.get("CollectionSweep")
    if collection_sweep is not None:
        beam_size = collection_sweep.beam_size
        if beam_size:
            row["beam diameter"] = max(beam_size)


def adjust_mxlims(
    objs: Dict[str, MxlimsObject],
    mapping:Dict[str, list[str]],
    row: Dict[str, Any]
):
    """Adjust contents of MxlimsObjects in place

    Allows for changes not possible with simple mapping"""
    beam_diameter = float(row.get("beam diameter"))
    if beam_diameter:
        beamsize = [beam_diameter, beam_diameter]
        objs["CollectionSweep"].beam_size = beamsize