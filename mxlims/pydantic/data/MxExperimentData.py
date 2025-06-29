# generated by datamodel-codegen:
#   filename:  data/MxExperimentData.json

from __future__ import annotations

from typing import Optional

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field, confloat, conint

from ..datatypes.SpaceGroupName import SpaceGroupName
from ..datatypes.UnitCell import UnitCell


class MxExperimentData(BaseModel):
    """
    Crystallography experiment, producing data
    """

    experiment_strategy: Optional[str] = Field(
        None,
        alias="experimentStrategy",
        description="Experiment strategy indicator",
        examples=[
            "OSC",
            "Helical",
            "MXPressE",
            "GPhL.native.basic",
            "GPhL.SAD.advanced",
            "GPhL.2wvlMAD.basic",
        ],
        title="Experiment Strategy",
    )
    expected_resolution: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="expectedResolution",
        description="The resolution expected in the experiment - for positioning the detector and setting up the experiment",
        title="Expected Resolution",
    )
    target_completeness: Optional[confloat(ge=0.0, le=100.0)] = Field(
        None,
        alias="targetCompleteness",
        description="Minimal completeness expected from experiment",
        title="Target Completeness",
    )
    target_multiplicity: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="targetMultiplicity",
        description="Minimal multiplicity expected from experiment",
        title="Target Multiplicity",
    )
    energy: Optional[confloat(ge=0.0)] = Field(
        None, description="Desired energy of the beam in eV", title="Energy"
    )
    dose_budget: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="doseBudget",
        description="Dose (MGy) to be used in experiment",
        title="Dose Budget",
    )
    radiation_sensitivity: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None,
        alias="radiationSensitivity",
        description="Predicted relative radiation sensitivity of sample at target wavelength.",
        title="Radiation Sensitivity",
    )
    snapshot_count: Optional[conint(ge=0)] = Field(
        0,
        alias="snapshotCount",
        description="Number of snapshots to acquire after each (re)centring",
        title="Snapshot Count",
    )
    wedge_width: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="wedgeWidth",
        description="Wedge width (in degrees) to use for interleaving",
        title="Wedge Width",
    )
    measured_flux: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="measuredFlux",
        description="Measured value of beam flux in photons/s",
        title="Measured Flux",
    )
    radiation_dose: Optional[confloat(ge=0.0)] = Field(
        None,
        alias="radiationDose",
        description="Total radiation dose absorbed during experiment",
        title="Radiation Dose",
    )
    expected_space_group_name: Optional[SpaceGroupName] = Field(
        None,
        alias="expectedSpaceGroupName",
        description="Name of space group expected to be present. Names may include alternative settings. Matches mmCIF item symmetry.space_group_name_H-M (https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_symmetry.space_group_name_H-M.html).",
        title="Space Group Name",
    )
    expected_unit_cell: Optional[UnitCell] = Field(
        None,
        alias="expectedUnitCell",
        description="Unit cell of crystal expected to be present.",
    )
    space_group_name: Optional[SpaceGroupName] = Field(
        None,
        alias="spaceGroupName",
        description="Name of space group, as determined during characterisation. Names may include alternative settings. Matches mmCIF item symmetry.space_group_name_H-M (https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_symmetry.space_group_name_H-M.html).",
        title="Space Group Name",
    )
    unit_cell: Optional[UnitCell] = Field(
        None,
        alias="unitCell",
        description="Unit cell of crystal, as determined during characterisation.",
    )
