#! /usr/bin/env python
# encoding: utf-8
""" Code generation for MXLIMS model - validating schemas against test files

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

__copyright__ = """ Copyright © 2026 -  MXLIMS collaboration."""
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"


import json
import jsonschema
from pathlib import Path
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
import traceback

MXLIMS_DIR = Path(__file__).parent.parent
from mxlims import __version__ as VERSION

def create_registry_from_directory(
        schema_dir=None, base_uri="https://mxlims.org/schemas/"
):
    """
    Recursively load all schemas from directory and subdirectories
    """

    if schema_dir is None:
        schema_dir = MXLIMS_DIR / "schemas"
    registry = Registry()

    # Use rglob to recursively find all .json files
    for schema_file in schema_dir.rglob("*.json"):
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        # Get relative path with forward slashes
        relative_path = schema_file.relative_to(schema_dir)
        relative_uri = str(relative_path).replace('\\', '/')  # Important for Windows!

        # Create absolute URI matching the $id pattern
        absolute_uri = base_uri + relative_uri

        resource = Resource.from_contents(schema, default_specification=DRAFT202012)

        # Register with the full path URI
        registry = registry.with_resource(uri=absolute_uri, resource=resource)

        # Also register with the $id from the schema if present
        if '$id' in schema:
            registry = registry.with_resource(uri=schema['$id'], resource=resource)

    return registry


def validate_file_path(fpath: Path, schema:str=None, valid=True) -> bool:
    """Validate JSON test file against matching schema

    If schema is None is assumed that the file is in the standard test file tree
    with standard naming conventions, and the 'valid; parameter is ignored

    :param fpath: test file to validate
    :param schema: schema to validate against - string like e.g. 'datatypes/UnitCell'
    :param valid: Should file validate as valid?
    :return: """
    if schema is None:
        parts = fpath.parts
        valstr = parts[-2]
        schemaname = parts[-3] + ".json"
        typdir = parts[-4]
    else:
        valstr = "valid" if valid else "invalid"
        typdir, schemaname = schema.split("/")
        schemaname += ".json"
    registry = create_registry_from_directory()
    passed = test_valid(fpath, registry, schemaname, typdir, valstr)
    if passed:
        print("Validation passed")
    else:
        print("Validation FAILED")
    return passed

def validate_all() -> None:
    """Validate schemas against all test files in directory tree

    Takes in files in .../all/ and in directory matching current version"""
    basedir = Path(__file__).resolve().parent.parent / "test" / "json"
    registry = create_registry_from_directory()
    for top in ("all", "v" + VERSION):
        topdir = basedir / top
        if topdir.is_dir():
            for fpath in topdir.rglob("*.json"):
                parts = fpath.parts
                valstr = parts[-2]
                schemaname = parts[-3] + ".json"
                typdir = parts[-4]
                test_passed = test_valid(fpath, registry, schemaname, typdir, valstr)
                if test_passed:
                    txt = "passed"
                else:
                    txt = "FAILED"
                filename = fpath.relative_to(basedir).as_posix()
                print (f"Test {txt} for {filename}")

    print ("\nAll other tests passed")

def test_valid(
        fpath: Path, registry: Registry, schemaname: str, typdir: str, valstr: str
) -> bool:
    """Validate fpath against typdir schema schemaname"""
    schemafile = Path(__file__).resolve().parent.parent / "schemas" / typdir / schemaname
    validity = (valstr == "valid")
    try:
        schema = json.load(open(schemafile))
        jsonschema.validate(instance=json.load(open(fpath)), schema=schema, registry=registry)
    except jsonschema.SchemaError as e:
        print("\nSCHEMA Error")
        print(traceback.format_exc())
        return False
    except jsonschema.ValidationError as e:
        if validity:
            print("\nVALIDATION ERROR")
            print(traceback.format_exc())
        return not validity
    return validity


if __name__ == "__main__":


    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(
        prog="validate_mxlims_model.py",
        formatter_class=RawTextHelpFormatter,
        prefix_chars="--",
        description="""
MXLIMS model validation and test. Assumes standard directory structure""",
    )

    parser.add_argument(
        "--testfile",
        metavar="testfile",
        default=None,
        help="""JSON file to test - if not set, validate all files
        If the file is not one of the standard test files the schemaname is required
        """,
    )

    parser.add_argument(
        "--schema",
        metavar="schema",
        default=None,
        help="""JSON schema to test against,
    e.g. 'messages/ShipmentMessage' or 'datatypes/UnitCell'.
    If not set the schema name is deduced from the testfile name,
    assuming that it is one of the standard testfiles in the standard location.
        """,
    )

    argsobj = parser.parse_args()
    options_dict = vars(argsobj)

    testfile = options_dict["testfile"]
    if testfile:
        fpath = Path(testfile).resolve()
        validate_file_path(fpath, schema=options_dict.get("schema"))

    else:
        validate_all()
