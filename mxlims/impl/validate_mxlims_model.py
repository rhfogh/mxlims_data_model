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
import os
from pathlib import Path
from ruamel.yaml import YAML
import subprocess
from subprocess import CalledProcessError
from typing import Optional, List

from mxlims.impl.MxlimsBase import camel_to_snake, CORETYPES
from mxlims.impl.generate_field_list import generate_fields

# pure=True uses yaml version 1.2, with fewer gotchas for strange type conversions
yaml = YAML(typ="safe", pure=True)
# The following are not needed for load, but define the default style.
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)

def validate_file_path(fpath: Path) -> bool:
    """Validate JSON test file against matching schema

    Standard naming conventions and directory structure are assumed"""
    parents = fpath.parents
    valstr = parents[0].stem
    typdir = parents[1].stem
    schemaname = fpath.stem.split("_")[0] + ".json"
    passed = test_valid(fpath, schemaname, typdir, valstr)
    if passed:
        print("Validation passed")

def validate_all() -> None:
    """Validate schemas against all test files in directory tree"""
    basedir = Path(__file__).resolve().parent.parent / "test" / "json"
    for typdir in ("datatypes", "objects", "messages"):
        for valstr in ("valid", "invalid"):
            dir1 = basedir / typdir / valstr
            for fpath in dir1.iterdir():
                schemaname = fpath.stem.split("_")[0] + ".json"
                test_valid(fpath, schemaname, typdir, valstr)
    print ("\nAll other tests passed")

def test_valid(fpath: Path, schemaname: str, typdir: str, valstr: str) -> bool:
    """Validate fpath against typdir schema schemaname"""
    schemafile = Path(__file__).resolve().parent.parent / "schemas" / typdir / schemaname
    validity = (valstr == "valid")
    commands = ["check-jsonschema", "--schemafile", schemafile.as_posix(), fpath.as_posix()]
    result = subprocess.run(commands)
    if validity == (not result.returncode):
        return True
    else:
        # Validation failed
        print (
            '\nValidation failed for %s'
            % "/".join((typdir, valstr, fpath.name))
        )
        return False

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
        help="JSON file to test - if not set validate all files\n",
    )

    argsobj = parser.parse_args()
    options_dict = vars(argsobj)

    testfile = options_dict["testfile"]
    if testfile:
        validate_file_path(Path(testfile).resolve())
    else:
        validate_all()

