# encoding: utf-8
""" Simple conversion to/from tab-separated column format

License:

The code in this file is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This code is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this file. If not, see <https://www.gnu.org/licenses/>.
"""

from importlib import import_module
from packaging import version
from pathlib import Path
from pydantic import BaseModel
from ruamel.yaml import YAML
from typing import List

from mxlims.impl.typemap import typemap

__copyright__ = """ Copyright © 2024 -  2025 MXLIMS collaboration."""
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

from typing import TYPE_CHECKING, Any, Dict, Tuple
if TYPE_CHECKING:
    from mxlims.pydantic.core.MxlimsObject import MxlimsObject
    from mxlims.pydantic.objects.Dataset import Dataset
    from mxlims.pydantic.objects.Job import Job
    from mxlims.pydantic.objects.LogisticalSample import LogisticalSample
    from mxlims.pydantic.objects.Sample import Sample

# pure=True uses yaml version 1.2, with fewer gotchas for strange type conversions
yaml = YAML(typ="safe", pure=True)
# The following are not needed for load, but define the default style.
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)

def import_spreadsheet(
         scheme:str, filepath:Path, separator="\t", result_mode: bool=False
):
    """Import spreadsheet-type file (e.g. comma- or tab-separated)

    with a line for each MXLIMS object in object_list.
    Note that this function makes assumptions to fit standard simple situations;


    For reading pre-experiment data (sample submission etc.) use result_mode False
    For reading acquired or processed data use result_mode True
    The difference is in how datasets are linked to jobs

    :param scheme: format and mapping to use, e.g. maxiv, soleil, ...
    :param filepath: Path of file to import, assumed to .csv or .tsv
    :param separator: Field separator in output file: "," or "\t"
    :param result_mode: If true link datasets as results, if false as input templates
    :return:
    """
    with open(filepath, "r") as fp0:
        data = [line.split(sep=separator) for line in fp0 if line.strip()]
    if len(data) <= 2:
        raise ValueError("MXLIMS requires at least header and data row")
    header = data.pop(0)
    for ll0 in data:
        if len(ll0) != len(header):
            raise ValueError(
                "Line has different number of fields than header:\n", ll0
            )
        ingest_row(dict(zip(header, ll0)), scheme, result_mode=result_mode)

def export_spreadsheet(
        object_list:List[MxlimsObject], scheme:str, filepath:Path, separator="\t"
):
    """Simplified export to spreadsheet-type file (e.g. comma- or tab-separated)

    with a line for each MXLIMS object in object_list.

    Note that this function makes assumptions to fit standard simple situations.

    The MxlimsObjects in the list are expanded to include linked-to objects.
    There can only be one object of each type and datasets are taken as results
    (if available) templates otherwise. This will only work for simple situations,
    e.g. not for multi-sweep experiments.

    For normal operation you should enter lists of Jobs or Result Datasets.
    Note that Samples and LogisticalSamples are NOT expanded to include Jobs or Datasets.



    :param object_list: MXLIMS objects determining what to export
    :param scheme: format and mapping to use, e.g. maxiv, soleil, ...
    :param filepath: Path of file to export to
    :param separator: Field separator in output file
    :return:
    """
    header, rows = generate_spreadsheet_data(object_list, scheme)
    lines = [separator.join(header)]
    for row in rows:
        lines.append(separator.join(row.get(tag, "") for tag in header))

    with open(filepath, "w") as fp0:
        fp0.write("\n".join(lines))

def ingest_row(data_dict: Dict[str, Any], scheme:str, result_mode: bool=False
) -> Dict[str, MxlimsObject]:
    """Convert list of tag, value data items to MxlimsObects according to scheme

    :param data_dict: Dictionary of tag: value data items
    :param scheme: format and mapping to use, e.g. maxiv, soleil, ...
    :param result_mode: If true link datasets as results, if false as input templates
    :return:
    """
    result = {}
    # Get newest version_dir with mappings
    version_dir = get_version_dir(scheme)
    dirname = version_dir.stem
    mapping : Dict[str, list[str]] = read_mapping(version_dir)
    adjust_mxlims = getattr(
        import_module(f"mxlims.conversion.{scheme}.{dirname}.converter"), "adjust_mxlims"
    )

    partials_dict: dict[int, dict[tuple, dict[str, Any]]] = {}
    for tag, val in data_dict.items():
        steps = mapping.get(tag)
        if steps:
            # Note unmapped items remain in data_dict for use in later adjustment
            last = steps[-1]
            partial = tuple(steps[:-1])
            length = len(partial)
            dd0 = partials_dict.get(length, {})
            partials_dict[length] = dd0
            dd1 = dd0.get(partial, {})
            dd0[partial] = dd1
            dd1[last] = val

    for length, dd0 in sorted(partials_dict.items(), reverse=True)[:-1]:
        # Start making objects and dicts, beginning at leaf end, and putting
        # them into dicts for containing objects
        for partial, dd1 in dd0.items():
            typ = typemap.get(partial)
            last = partial[-1]
            tpl = partial[:-1]
            if typ is None:
                raise ValueError(
                    f"Unknown type '{partial}' in mapping for version {version_dir}"
                )
            else:
                dd0 = partials_dict.get(length-1, {})
                partials_dict[length-1] = dd0
                dd3 = dd0.get(tpl, {})
                dd0[tpl] = dd3
                if issubclass(typ, dict):
                    # Type is a dictionary - put it in the containing object
                    dd3[last] = dd1
                elif issubclass(typ, BaseModel):
                    # Presumably a Datatype
                    dd3[last] = typ(**dd1)
                else:
                    raise RuntimeError(f"Cannot handle type '{typ}'")

    # All data have now been passed to MxlimsObject inputs (length == 1)
    # Make them
    for tpl, dd0 in partials_dict[1].items():
        mxlims_type = tpl[0]
        mxlimsobj = getattr(
            import_module(f"mxlims.pydantic.objects.{mxlims_type}"), mxlims_type
        )
        result[mxlims_type] = mxlimsobj(**dd0)
    #
    adjust_mxlims(result, mapping, data_dict)
    link_mxlims_objects(result, result_mode)
    return result

def link_mxlims_objects(result: Dict[str, MxlimsObject], result_mode:bool= False):
    """Set links between MxlimsObjects in result according to standard assumed pattern

    Specific to MX type data, not generic

    :param result:
    :param result_mode: Determines if Datasets are treated as results (if True) or input templates
    :return:
    """
    mxlims_dir = Path(__file__).resolve().parent.parent
    link_refs = yaml.load(mxlims_dir / "mxlims" / "impl" / "link_specification.yaml")

    # Set up samples:
    sample = result.get("MacromoleculeSample")
    if sample:
        sample.medium = result.get("Medium")
        sample.mainComponent = result.get("Macromolecule")

    # Set up LogisticalSamples
    logistical_samples = list(
        obj for obj in result.values() if isinstance(obj, LogisticalSample)
    )
    for obj in logistical_samples:
        container_link = link_refs[obj.mxlims_type]["links"].get("container")
        if container_link:
            for ctype in container_link["typenames"]:
                container = result.get(ctype)
                if container is not None:
                    # NB .container is settable in ALL cases that could reach this point
                    # i.e. is for all LogisticalSamples except Shipment
                    obj.container = container
                    break
    leaf_containers = [obj for obj in logistical_samples if not obj.contents]
    if len(leaf_containers) == 1:
        leaf_container = leaf_containers[0]
    else:
        leaf_container = None

    # Set up Jobs
    mx_experiment = result.get("MxExperiment")
    mx_processing = result.get("MxProcessing")
    for job in (mx_experiment, mx_processing):
        if job is not None:
            if sample is not None:
                job.sample = sample
            if leaf_container is not None:
                job.logistical_sample = leaf_containers

    # Set up datasets
    dataset = result.get("CollectionSweep")
    if dataset is not None:
        if leaf_container is not None:
            dataset.logistical_sample = leaf_container
        if mx_experiment is not None:
            if result_mode:
                dataset.source = mx_experiment
            else:
                mx_experiment.template_data = [dataset]
    dataset = result.get("ReflectionSet")
    if dataset is not None:
        if leaf_container is not None:
            dataset.logistical_sample = leaf_container
        if mx_processing is not None:
            if result_mode:
                dataset.source = mx_processing
            else:
                mx_processing.template_data = [dataset]


def generate_spreadsheet_data(
        object_list:List[MxlimsObject], scheme:str
) -> Tuple[list, List[dict]]:
    """Export spreadsheet-type file (e.g. comma- or tab-separated)

    with a line for each MXLIMS object in object_list

    :param object_list: MXLIMS objects determining what to export
    :param scheme: format and mapping to use, e.g. maxiv, soleil, ...
    :return:
    """
    version_dir = get_version_dir(scheme, version.parse(object_list[0].version))
    dirname = version_dir.stem
    mapping : Dict[str, list[str]] = read_mapping(version_dir)
    adjust_row = getattr(
        import_module(f"mxlims.conversion.{scheme}.{dirname}.converter"), "adjust_row"
    )

    header : list[str] = list(mapping)
    data : List[Dict[str,Any]]= []
    # get dict of relevant MxlimsObjects
    for obj in object_list:
        if isinstance(obj, Job):
            objs = expand_job(obj)
        elif isinstance(obj, Dataset):
            objs = expand_dataset(obj)
        elif isinstance(obj, LogisticalSample):
            objs = expand_logistical_sample(obj)
        elif isinstance(obj, Sample):
            objs = expand_sample(obj)
        else:
            raise ValueError(
                "Input object must be a Job, Dataset, LogisticalSample, or Sample"
            )
        row = get_row(objs, mapping)
        adjust_row(objs, mapping, row)
        data.append(row)

    return header, data

def get_row(
        objs: Dict[str, MxlimsObject], mapping:Dict[str, list[str]]
) -> Dict[str, Any]:
    """Get row-data dictionary from MxlimsObjects and mapping

    NB for unresolvable mappings will put in an intermediate value
    that must eb fixed at teh adjustment state (or avoided in the mapping)"""
    result = {}
    for tag, steps in mapping.items():
        obj = objs.get(steps[0])
        if obj is None:
            continue
        for step in steps[1:]:
            if obj is None:
                # No object/value found
                break
            elif isinstance(obj, dict):
                # obj is a dictionary - use next string as a key
                obj = obj.get(step)
            elif hasattr(obj, step):
                # Obj is an MxlimsObjetc or datatype, or anyway has the right attribute
                obj=getattr(obj, step)
            else:
                # obj is NOT mappable (e.g. a list of Datatypes) - potential error
                # This value must be adjusted later or avoided in the mapping
                break
        if obj is None:
            continue
        else:
            result[tag] = obj
    return result


def get_version_dir(scheme:str, mxlims_version: version.Version=None) -> Path:
    """Get version directory path name for a given scheme and mxlims_version"""
    mxlims_dir = Path(__file__).resolve().parent.parent
    scheme_dir = mxlims_dir / "conversion" / scheme
    subdirs = [x for x in scheme_dir.iterdir() if x.is_dir()]
    version_map = {}
    subdir = None
    for subdir in subdirs:
        vrs = version.parse(subdir.name.replace("_", "."))
        version_map[vrs] = subdirs
    if mxlims_version:
        for vrs,subdir in sorted(version_map.items()):
            if vrs > mxlims_version:
                break
        if subdir is None:
            raise RuntimeError(f"Version directory for scheme {scheme} not found")
    elif version_map:
        subdir = sorted(version_map.items())[-1][1]
    else:
        raise RuntimeError(f"No version directories found for scheme {scheme}")
    return scheme_dir / subdir

def read_mapping(version_dir: Path) -> dict[str, list[str]]:
    """Read scheme-specific mapping file from version_dir and convert to dict[str, tuple]"""

    file = None
    sep = "\t"
    for file in version_dir.iterdir():
        if file.name in ("mapping.tsv", "mapping.csv"):
            if file.suffix == "csv":
                sep = ","
            break
    if file is None:
        raise RuntimeError(f"Mapping file not found in {version_dir.as_posix()}")
    result = {}
    with open(version_dir / file, "r") as fp0:
        for line in fp0:
            column, addr, comment = line.split(sep)
            if addr != "MXLIMS":
                # Skipping first, header line
                result[column] = addr.split(".")
    #
    return result


def expand_job(source: Job)  -> dict[str, MxlimsObject]:
    """Make dictionary with one object of each relevant type, starting from any Job

    :param source:  object to expand
    """
    result = {}
    result[source.mxlims_type] = source
    sample = source.sample
    if sample:
        result.update(expand_sample(sample))
    logistical_sample = source.logistical_sample
    if logistical_sample:
        new_data = expand_logistical_sample(logistical_sample)
        new_data.update(result)
        result = new_data

    # Get Dataset, either result (if any) or template
    dataset = None
    for dataset in source.results:
        if dataset.role == "Result":
            break
    else:
        template_data = source.template_data
        if len(template_data) == 1:
            dataset = template_data[0]
    if dataset:
        result[dataset.mxlims_type] = dataset

    # Read experiment from input-creating job, if any
    # input_job taken from input links, or if only MxExperiment on same sample
    # The latter is a heuristic only, but this is a simplified conversion scheme
    input_job = None
    input_jobs = set(dataset.source for dataset in source.input_data if dataset)
    if len(input_jobs) == 1:
        input_job = input_jobs.pop()
    elif source.mxlims_type == "MxProcessing":
        # NBNB This is NOT generic. Cannot be helped.
        obj = source.logistical_sample or source.sample
        exps = list(job for job in obj.jobs if job.mxlims_type == "MxExperiment")
        if len(exps) == 1:
            input_job = exps[0]
    if input_job is not None:
        inp_data = expand_job(input_job)
        # Data from this job override the same objects from input Job
        inp_data.update(result)
        result = inp_data
    #
    return result

def expand_dataset(source: Dataset) -> dict[str, MxlimsObject]:
    """Make dictionary with one object of each relevant type, starting from any Dataset

    :param source:  object to expand
    """
    result = {}
    result[source.mxlims_type] = source
    logistical_sample = source.logistical_sample
    if logistical_sample:
        result.update(expand_logistical_sample(logistical_sample))
    job = source.source
    if job:
        job_data = expand_job(job)
        job_data.update(result)
        result = job_data
    #
    return result

def expand_logistical_sample(source: LogisticalSample) -> dict[str, MxlimsObject]:
    """Make dictionary with one object of each relevant type, starting from any LogisticalSample

    :param source:  object to expand
    """
    result = {}
    logistical_sample = source
    sample = None
    while logistical_sample:
        result[logistical_sample.mxlims_type] = logistical_sample
        if not sample:
            sample = logistical_sample.sample
        logistical_sample = logistical_sample.container
    if sample:
        result.update(expand_sample(sample))
    #
    return result


def expand_sample(source: Sample) -> dict[str, MxlimsObject]:
    """Make dictionary with one object of each relevant type, starting from any Sample

    :param source:  object to expand
    """
    result = {}
    result[source.mxlims_type] = source
    main_component = source.main_component
    if main_component and main_component.mxlims_type not in result:
        result[main_component.mxlims_type] = main_component
    medium = source.medium
    if medium and medium.mxlims_type not in result:
        result[medium.mxlims_type] = medium
    return result