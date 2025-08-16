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

__copyright__ = """ Copyright © 2024 -  2025 MXLIMS collaboration."""
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

from typing import TYPE_CHECKING, Any, Dict, get_origin, get_args
if TYPE_CHECKING:
    from mxlims.impl.MxlimsBase import MxlimsImplementation
    from mxlims.pydantic.objects.Dataset import Dataset
    from mxlims.pydantic.objects.Job import Job
    from mxlims.pydantic.objects.LogisticalSample import LogisticalSample
    from mxlims.pydantic.objects.Sample import Sample


def dict2mxlims(mapping: Dict[str,str], values: Dict[str, Any]) -> Dict[str, MxlimsImplementation]:
    """Convert single-dictionary values to MXLIMS using mapping dictionary

    """
    dict1 = {}
    result = {}
    # Put value (last step) into dictionary, and key by first part of addr
    for tag, val in values.items():
        if val is not None:
            addr = mapping.get(tag)
            if addr is None:
                raise ValueError("tag %s not supported in MXLIMS mapping" % tag)
            steps = addr.split(".")
            key1 = tuple(steps[:-1])
            dict2 = dict1.get(key1, {})
            dict2[steps[-1]] = val
            dict1[key1] = dict2

    for key, kwargs in reversed(dict1.items()):
        # Put MxlimsObjects into result
        if len(key) == 1:
            del dict1[key]
            clsname = key[0]
            cls = getattr(import_module(f"mxlims.pydantic.objects.{clsname}"), clsname)
            result[clsname] = cls(**kwargs)

    for key, kwargs in reversed(dict1.items()):
        # Put MxlimsObjects into result
        if len(key) == 2:
            del dict1[key]
            clsname = key[0]
            cls = getattr(import_module(f"mxlims.pydantic.objects.{clsname}"), clsname)
            fieldname = key[1]
            annotation = cls.model_fields[fieldname].annotation






            result[clsname] = cls(**kwargs)

def get_annotation_type(annotation):
    


def mxlims2dict(mapping: Dict[str,str], objects: Dict[str, MxlimsImplementation]) -> Dict[str, Any]:
    """Extract values from MXLIMS using mapping dictionary

    Typical use to generate a single-line data representation for e.g. an upload spreadsheet

    The values in the mapping dictionary are of the form
    <MxlimsType>.tag1.tag2 etc.
    where tag1, tag2 are either attribute names (if the preceding value is an object)
    or dictionary keys (if teh preceding value is a dictionary, e.g. for fields like
    'identifiers'

    NB This function cannot work for fields that are lists of objects,
    such as Sample.components, CollectionSweep.scans,
    ReflectionSet.reflection_statistics_shells, or namespaced_extensions

    :param mapping: Dictionary of column name to MXLIMS mapping tag,
    :param objects: Dictionary of column name to value extracted from MXLIMS
    :return:
    """
    result ={}
    for tag, addr in mapping.items():
        # NB This will NOT work
        target = objects
        for step in addr.split("."):
            if target is None:
                break
            elif isinstance(target, dict):
                target = target.get(step)
            else:
                target = getattr(target, step)
        if target is not None:
            result[tag] = target
    #
    return result

def expand_job(source: Job)  -> dict[str, MxlimsImplementation]:
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

    # Read data from input-creating job, if any
    input_jobs = set(dataset.source for dataset in source.input_data if dataset)
    if len(input_jobs) == 1:
        input_job = input_jobs.pop()
        inp_data = expand_job(input_job)
        # Data from this job override the same objects from input Job
        inp_data.update(result)
        result = inp_data
    #
    return result

def expand_dataset(source: Dataset) -> dict[str, MxlimsImplementation]:
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

def expand_logistical_sample(source: LogisticalSample) -> dict[str, MxlimsImplementation]:
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


def expand_sample(source: Sample) -> dict[str, MxlimsImplementation]:
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