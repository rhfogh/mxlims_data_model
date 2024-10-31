#! /usr/bin/env python
# encoding: utf-8
#
"""

License:

This file is part of the MXLIMS collaboration.

MXLIMS models and code are free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MXLIMS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with MXLIMS. If not, see <https://www.gnu.org/licenses/>.
"""

__copyright__ = """ Copyright © 2024 -  2024 MXLIMS collaboration."""
__author__ = "rhfogh"
__date__ = "18/10/2024"


import enum
from typing import Optional, Dict, List, Tuple, Union

from pydantic import BaseModel, Field

from mxlims.pydantic.core import Job, Dataset, PreparedSample, LogisticalSample


class PdbxSignalType(str, enum.Enum):
    """Observability criterion. Matches mmCIF refln.pdbx_signal_status"""

    I_over_sigma = "local <I/sigmaI>"
    wCC_half = "local wCC_half"


class QualityFactorType(str, enum.Enum):
    """Name for quality factor type, used in QualityFactor class"""

    R_merge = "R(merge)"
    R_meas = "R(meas)"
    R_pim = "R(pim)"
    I_over_SigI = "I/SigI"
    CC_half = "CC(1/2)"
    CC_ano = "CC(ano)"
    SigAno = "SigAno"
    Completeness = "Completeness"
    Redundancy = "Redundancy"


class ReflectionBinningMode(str, enum.Enum):
    """Reflection binning mode for binning reflection statistics"""

    equal_volume = "equal_volume"
    equal_number = "equal_number"
    dstar_equidistant = "dstar_equidistant"
    dstar2_equidistant = "dstar2_equidistant"


class UnitCell(BaseModel):
    """Crystallographic unit cell"""

    a: float = Field(
        frozen=True,
        json_schema_extra={"description": "A axis length (A)"},
    )
    b: float = Field(
        frozen=True,
        json_schema_extra={"description": "B axis length (A)"},
    )
    c: float = Field(
        frozen=True,
        json_schema_extra={"description": "C axis length (A)"},
    )
    alpha: float = Field(
        frozen=True,
        json_schema_extra={"description": "alpha angle (degres)"},
    )
    beta: float = Field(
        frozen=True,
        json_schema_extra={"description": "beta angle (degres)"},
    )
    gamma: float = Field(
        frozen=True,
        json_schema_extra={"description": "gamma angle (degres)"},
    )


class Tensor(BaseModel):
    """Tensor"""

    eigenvalues: Tuple[float, float, float] = Field(
        json_schema_extra={"description": "of tensor"},
    )
    eigenvectors: List[Tuple[float, float, float]] = Field(
        json_schema_extra={
            "description": "Eigenvectors (unit vectors) of tensoer, "
            "in same order as eigenvalues"
        },
    )


class QualityFactor(BaseModel):
    """Reflection shell quality factor. Enumerated type with associated value"""

    type: QualityFactorType = Field(
        json_schema_extra={"description": "Quality factor type"},
    )
    value: float = Field(
        json_schema_extra={"description": "Quality factor value"},
    )

class Macromolecule(BaseModel):
    """Macromolecule - main molecule under investigation

    #NB model still incomplete"""
    acronym: str = Field(
        json_schema_extra={
            "description": "Acronynm - short synonym of macromolecule"
        },
    )
    name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Human readable name of macromolecule"
        },

    )
    identifiers: Dict[str, str] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Dictionary of contextName: identifier."
            "contectName could refer to a LIMS, database, or web site "
            "but could also be e.g. 'sequence'",
        },
    )

class Component(BaseModel):
    """Additional component of sample ('ligand')

    #NB model still incomplete"""
    acronym: str = Field(
        json_schema_extra={
            "description": "Acronynm - short synonym of component (e.g. 'lig1'"
        },
    )
    name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Human readable name of component"
        },

    )
    identifiers: Dict[str, str] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Dictionary of contextName: identifier."
            "contectName will typically refer to a LIMS, database, or web site "
            "but could also be e.g. 'smiles'",
        },
    )


class MXExperiment(Job):
    """MX Crystallographic data acquisition experiment."""

    experiment_strategy: str = Field(
        default=None,
        json_schema_extra={
            "description": "Experiment strategy indicator",
            "examples": [
                "OSC",
                "Helical",
                "MXPressE",
                "GPhL_native_basic",
                "GPhL_SAD_advanced",
                "GPhL_2wvl_basic",
            ],
        },
    )
    expected_resolution: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "The resolution expected in the experiment "
            "– for positioning the detector and setting up the experiment"
        },
    )
    target_completeness: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Minimal completeness expected from experiment",
        },
    )
    target_multiplicity: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Minimal multiplicity expected from experiment",
        },
    )
    dose_budget: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Dose (MGy) to be used in experiment",
        },
    )
    snapshot_count: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "description": "Number of snapshots to acquire after each (re)centring",
        },
    )
    wedge_width: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Wedge width (in degrees) to use for interleaving",
        },
    )
    measured_flux: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Measured value of beam flux in photons/s",
        },
    )
    radiation_dose: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Total radiation dose absorbed during experiment",
        },
    )
    unit_cell: Optional[UnitCell] = Field(
        default=None,
        json_schema_extra={
            "description": "Crystallographic unit cell, "
            "as determined during charaterisation",
        },
    )
    space_group_name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Name of space group, as determined during characterisation. "
            "Names may include alternative settings.",
        },
    )
    # Overriding superclass fields, for more precise typing
    sample: Optional["MXSample"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "MX Crystallographic sample relevant to Job."
            "return link for MXSample.jobs"
        },
    )
    results: List["CollectionSweep"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "CollectionSweeps produced by Job",
        },
    )
    templates: List["CollectionSweep"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "CollectionSweeps input templates for Job",
        },
    )
    reference_data: List["ReflectionSet"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Reference ReflectionSets for Job",
        },
    )


class CollectionSweep(Dataset):
    """
   MX  Crystallographic data collection sweep, may be subdivided for acquisition

    Note that the CollectionSweep specifies a single, continuous sweep range,
    with equidistant images given by image_width, and all starting motor positions
    in axis_position_start. axis_positions_end contain the end point of the sweep,
    and must have at least the value for the scan_axis; sweeps changing more than
    one motor (e.g. helical scan) can be represented by adding more values
    to axis_positions_end. The default number of images can be calculated from the
    sweep range and image_width. The actual number of images, the image numbering,
    and the order of acquisition (including interleaving) follows from the list of
    Scans. The role should be set to ‘Result’ for those sweeps that are deemed to
    be the desired result of the experiment; in templates you would prefer to use
    Acquisition for the Dataset that gives the acquisition parameters.
    """

    annotation: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Annotation string for sweep",
        },
    )
    exposure_time: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Exposure time in seconds",
        },
    )
    image_width: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Width of a single image, along scan_axis. "
            "For rotational axes in degrees, for translations in m.",
        },
    )
    energy: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Energy of the beam in eV",
        },
    )
    transmission: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        json_schema_extra={
            "description": "Transmission setting in %",
        },
    )
    detector_type: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Type of detector, "
            "using enumeration of mmCIF Items/_diffrn_detector.type.html",
        },
    )
    detector_binning_mode: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Binning mode of detector. "
            "Should be made into an enumeration",
        },
    )
    detector_roi_mode: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Region-of-interest mode of detector. "
            "Should be made into an enumeration",
        },
    )
    beam_position: Optional[Tuple[float, float]] = Field(
        default=None,
        json_schema_extra={
            "description": "x,y position of the beam on the detector in pixels",
        },
    )
    beam_size: Optional[Tuple[float, float]] = Field(
        default=None,
        json_schema_extra={
            "description": "x,y size of the beam on the detector in m",
        },
    )
    beam_shape: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Shape of the beam. NBNB Should be an enumeration",
            "examples": ["unknown", "rectangular", "ellipsoid"],
        },
    )
    axis_positions_start: Dict[str, float] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Starting position of axes, rotations or translations, "
            "including detector distance, by name. "
            "Units are m for distances, degrees for angles",
        },
    )
    axis_positions_end: Dict[str, float] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Final position of all scanned axes, as for axis_positions_start,"
            "NB scans may be acquired out of order, so this determines the limits "
            "of the sweep, not the temporal start and end points",
        },
    )
    scan_axis: str = Field(
        json_schema_extra={
            "description": "Name of main scanned axis. "
            "Other axes may be scanned in parallel."
            "",
            "examples": [
                "Omega",
                "Kappa",
                "Phi",
                "Chi",
                "TwoTheta",
                "SampleX",
                "SampleY",
                "SampleZ",
                "DetectorX",
                "DetectorY",
            ],
        }
    )
    overlap: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Overlap between successivce images, in degrees. "
            "May be negtive for non-contiguous images.",
        },
    )
    num_triggers: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "description": "Number of triggers. Instruction to detector "
            "- does not modify effect of other parameters.",
        },
    )
    num_images_per_trigger: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "description": "Number of images per trigger. Instruction to detector "
            "- does not modify effect of other parameters.",
        },
    )
    scans: List["Scan"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "List of Snas i.e. subdivisions of CollectionSweep"
            "NB Scans need not be contiguous or in order or add up to entire sweep",
        },
    )
    file_type: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Type of file.",
            "examples": ["mini-cbf", "imgCIF", "FullCBF", "HDF5", "MarCCD"],
        },
    )
    prefix: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Input parameter - used to build the fine name template.",
        },
    )
    filename_template: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "File name template,  includes prefix, suffix, "
            "run number, and a slot where image number can be filled in.",
        },
    )
    path: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Path to directory containing image files.",
        },
    )
    # Overriding superclass fields, for more precise typing
    source: Optional["MXExperiment"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "MXExperiment that created this Dataset. return link for job.results"
        },
    )


class Scan(BaseModel):
    """Subdivision of CollectionSweep

    The Scan describes a continuously acquired set of images that forms a subset of the
    CollectionSweep of which they form part. The ordinal gives the acquisition order of
    sweeps across an entire multi-sweep experiment; this allows you to describe
    out-of-order acquisition and interleaving.
    """

    scan_position_start: float = Field(
        json_schema_extra={
            "description": "Value of scan axis for the first image, "
            "in units matching axis type",
        }
    )
    first_image_no: int = Field(
        json_schema_extra={
            "description": "Image number to use for first image",
        }
    )
    num_images: int = Field(
        json_schema_extra={
            "description": "Number of images to acquire as part of the Scan.",
        }
    )
    ordinal: int = Field(
        json_schema_extra={
            "description": "Ordinal defining the ordering of all scans within the "
            "experiment (not just within the scan)",
        }
    )


class MXProcessing(Job):
    """MX Crystallographic processing calculation, going from images to reflection sets"""

    unit_cell: Optional[UnitCell] = Field(
        default=None,
        json_schema_extra={
            "description": "Expected unit cell for processing.",
        },
    )
    space_group_name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Name of expected space group, for processing. "
            "Names may include alternative settings.",
        },
    )
    # Overriding superclass fields, for more precise typing
    sample: Optional["MXSample"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "MX Crystallographic sample relevant to Job."
            "return link for MXSample.jobs"
        },
    )
    input_data: List[CollectionSweep] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Input data sets (pre-existing), used for calculation",
        },
    )
    results: List["ReflectionSet"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Datasets produced by Job",
        },
    )
    templates: List["ReflectionSet"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "CollectionSweeps input templates for Job",
        },
    )
    reference_data: List["ReflectionSet"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Reference ReflectionSets for Job",
        },
    )


class ReflectionStatistics(BaseModel):
    """Reflection statistics for a shell (or all) of reflections"""

    resolution_limits: Tuple[float, float] = Field(
        json_schema_extra={
            "description": "lower, higher resolution limit fo shell "
            "– matches mmCIF d_res_high, d_res_low.",
        }
    )
    number_observations: int = Field(
        json_schema_extra={
            "description": "total number of observations, "
            "– NBNB matches WHICH mmCIF parameter?",
        }
    )
    number_unique_observations: int = Field(
        json_schema_extra={
            "description": "total number of unique observations, "
            "– NBNB matches WHICH mmCIF parameter?",
        }
    )
    quality_factors: List[QualityFactor] = Field(
        default_factory=list,
        json_schema_extra={"description": "Quality factors for reflection shell, "},
    )
    completeness: float = Field(
        ge=0.0,
        le=100.0,
        json_schema_extra={
            "description": "Completeness for reflection shell in %, "
            "matches mmCIF percent_possible_all. NBNB What about ...._obs??"
        },
    )
    chi_squared: Optional[float] = Field(
        default=None,
        ge=0.0,
        json_schema_extra={
            "description": "Chi-squared statistic for reflection shell, "
            "matches mmCIF pdbx_chi_squared"
        },
    )
    number_rejected_reflns: Optional[int] = Field(
        default=None,
        json_schema_extra={
            "description": "Number of rejected reflns for reflection shell, "
            "matches pdbx_rejects"
        },
    )
    redundancy: float = Field(
        ge=0.0,
        json_schema_extra={
            "description": "Redundancy of data collected in this shell "
            "– matches mmCIF pdbx_redundancy"
        },
    )
    redundancy_anomalous: float = Field(
        ge=0.0,
        json_schema_extra={
            "description": "Redundancy of anomalous data collected in this shell "
            "– matches mmCIF pdbx_redundancy_anomalous"
        },
    )


class ReflectionSet(Dataset):
    """Processed, "Processed reflections, possibly merged or scaled

    as might be stored within an MTZ file or as mmCIF.refln"""

    anisotropic_diffraction: bool = Field(
        default=False,
        json_schema_extra={
            "description": "Is diff4raction limit analysis aniosotropic? True/False ",
        },
    )
    resolution_rings_detected: List[Tuple[float, float]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Resolution rings detected as originating from ice, powder "
            "diffraction etc.",
        },
    )
    resolution_rings_excluded: List[Tuple[float, float]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Resolution rings excluded from calculation",
        },
    )
    unit_cell: Optional[UnitCell] = Field(
        default=None,
        json_schema_extra={
            "description": "Unit cell determined.",
        },
    )
    space_group_name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Name of detected space group. "
            "Names may include alternative settings.",
        },
    )
    operational_resolution: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Operation resolution in A matchingobserved_criteria.",
        },
    )
    B_iso_Wilson_estimate: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "matches mmCIF reflns.B_iso_Wilson_estimate",
        },
    )
    h_index_range: Tuple[int, int] = Field(
        json_schema_extra={
            "description": "lowest and higherst h index - matches mCIF reflens.limit_h_*",
        }
    )
    k_index_range: Tuple[int, int] = Field(
        json_schema_extra={
            "description": "lowest and higherst k index - matches mCIF reflens.limit_h_*",
        }
    )
    l_index_range: Tuple[int, int] = Field(
        json_schema_extra={
            "description": "lowest and higherst l index - matches mCIF reflens.limit_h_*",
        }
    )
    num_reflections: int = Field(
        json_schema_extra={
            "description": "Total number of reflections - matches mmCIF ???? "
        }
    )
    num_unique_reflections: int = Field(
        json_schema_extra={
            "description": "Total number of unique reflections - matches mmCIF ???? "
        }
    )
    aniso_B_tensor: Optional[Tensor] = Field(
        default=None,
        json_schema_extra={
            "description": "Anisotropic B tensor, matching mmCIF reflns.pdbx_aniso_B_tensor"
        },
    )
    diffraction_limits_estimated: Optional[Tensor] = Field(
        default=None,
        json_schema_extra={
            "description": "Ellipsoid of observable reflections (unit:A), "
            "regardless whether all have actually been observed. "
            "Matches mmCIF reflns.pdbx_anisodiffraction_limit",
        },
    )
    overall_refln_statistics: Optional[ReflectionStatistics] = Field(
        default=None,
        json_schema_extra={
            "description": "Reflection statistics for all measured reflections",
        },
    )
    refln_shells: List[ReflectionStatistics] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Reflection statistics per reflection shell",
        },
    )
    observed_criterion_sigma_F: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Criterion for when a reflection counts as observed, as a "
            "multiple of sigma(F) – matches mmCIF reflns.observed_criterion_sigma_F",
        },
    )
    observed_criterion_sigma_I: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Criterion for when a reflection counts as observed, as a "
            "multiple of sigma(I) – matches mmCIF reflns.observed_criterion_sigma_I",
        },
    )
    signal_type: Optional[PdbxSignalType] = Field(
        default=None,
        json_schema_extra={
            "description": "local <I/sigmaI>’, ‘local wCC_half'; "
            "matches reflns.pdbx_signal_type. Criterion for observability, "
            "as used in mmCIF revln.pdbx_signal_status"
        },
    )
    signal_cutoff: Optional[float] = Field(
        default=None,
        json_schema_extra={
            "description": "Limiting value for signal calculation; "
            "matches reflns.pdbx_observed_signal_threshold. Cutoff for observability, "
            "as used in mmCIF refln.pdbx_signal_status"
        },
    )
    resolution_cutoffs: List[QualityFactor] = Field(
        default_factory=list,
        json_schema_extra={"description": "MRFANA resolution cutoff criteria"},
    )
    binning_mode: Optional[ReflectionBinningMode] = Field(
        default=None,
        json_schema_extra={"description": "Binning mode for reflection binning"},
    )
    number_bins: Optional[int] = Field(
        default=None,
        gt=0,
        json_schema_extra={
            "description": "Number of equal volume bins for reflection binning"
        },
    )
    refln_per_bin: Optional[int] = Field(
        default=None,
        gt=0,
        json_schema_extra={"description": "Number of reflections per bin"},
    )
    refln_per_bin_per_sweep: Optional[int] = Field(
        default=None,
        gt=0,
        json_schema_extra={
            "description": "Number of reflections per bin for per-run statistics"
        },
    )
    file_type: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Type of file NBNB Should be enum What values??",
        },
    )
    filename: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "File name NBNB What about multiple files?.",
        },
    )
    path: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Path to directory containing reflection set files.",
        },
    )
    # Fields overriding superclass for more precise typing
    source: Optional["MXProcessing"] = Field(
        default=None,
        frozen=True,
        json_schema_extra={
            "description": "Job that created this Dataset. return link for job.results"
        },
    )


class MXSample(PreparedSample):
    """Prepared Sample with MX crystallography-specific additions"""

    unit_cell: Optional[UnitCell] = Field(
        default=None,
        json_schema_extra={
            "description": "Unit cell expected in sample.",
        },
    )
    space_group_name: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Name of space group expected in Sample. "
            "Names may include alternative settings.",
        },
    )
    radiation_sensitivity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        json_schema_extra={"description": "Relative radiation sensitivity of sample."},
    )
    identifiers: Dict[str, str] = Field(
        default_factory=dict,
        json_schema_extra={
            "description": "Dictionary of contextName: identifier."
            "contectName will typically refer to a LIMS, database, or web site "
            "and the identifier will point to the ample within thie context",
            "examples": [
                {'sendersId':'29174',
                 'receiversUrl':'http://lims.synchrotron.org/crystal/54321'
                },
            ],
        },
    )
    jobs: List[Union[MXExperiment, MXProcessing]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Jobs (templates, planned, initiated or completed)"
            "for this PreparedSample",
        },
    )

class MXLogisticalSample(LogisticalSample):
    """Logistical Sample (crystal, location, ...) with MX crystallography-specific additions
"""
    sample: Optional["MXSample"] = Field(
        default=None,
        json_schema_extra={
            "description": "The sample preparation that applies "
            "to this MXLogisticalSample and all its contents",
        },
    )
    container: Optional["LogisticalSample"] = Field(
        default=None,
        json_schema_extra={
            "description": "The LogisticalSample containing this one",
        },
    )
    contents: List["LogisticalSample"] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Do not use - MXLogisticalSamples should not have contents",
        },
    )
    jobs: List[Union[MXExperiment, MXProcessing]] = Field(
        default_factory=list,
        json_schema_extra={
            "description": "Jobs (templates, planned, initiated or completed)"
            "for this MXLogisticalSample",
        },
    )

if __name__ == "__main__":
    # Usage:
    # python -m mxlims.pydantic.crystallography
    import json
    schema = MXLogisticalSample.model_json_schema()
    fp = open("MXLogisticalSample_schema.json", "w")
    json.dump(schema, fp, indent=4)

    # To generate html odcumentation use
    # generate-schema-doc --link-to-reused-ref MXLogisticalSample_schema.json ../jsonDocs

