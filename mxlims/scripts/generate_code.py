#! /usr/bin/env python
# encoding: utf-8
""" Code generation for MXLIMS model

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

__copyright__ = """ Copyright © 2016 - 2025 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

import json
import os
from pathlib import Path
from typing import Optional

# Templates

json_reference_template = """{{
    "$schema": "https://json-schema.org/draft-07/schema",
    "description": "Reference to {name}",
    "title": "{name}Ref",
    "type": "object",
    "properties": {{
        "mxlimsType": {{
            "description": "The type of the MXLIMS object referred to.",
            "title": "MxlimsType",
            "type": "string",
            "const": "{name}"
        }},
        "#ref": {{
            "description": "JSON reference to object in std. message, using uuid-based links.",
            "title": "JSONreference",
            "type": "string",
            "pattern": "^/{name}/[a-fA-F0-9]{{8}}-?[a-fA-F0-9]{{4}}-?[1-5][a-fA-F0-9]{{3}}-?[89abAB][a-fA-F0-9]{{3}}-?[a-fA-F0-9]{{12}}$"
        }}
    }},
    "required": [
        "ref"
    ],
    "additionalProperties": false
}}
"""

def generate_mxlims(dirname: Optional[str] = None) -> None :
    """
    Generate MXLIMS references JSON files and objects/ pydantic files

    :param dirname: path to mxlims wor4king directory
    :return:
    """
    if dirname:
        mxlims_dir = Path(dirname)
    else:
        mxlims_dir = Path.cwd()
    objects = load_schemas(mxlims_dir / "mxlims" / "schemas" / "objects")
    references = make_json_references(
        mxlims_dir / "mxlims" / "schemas" / "references", objects
    )

def load_schemas(schema_dir: Path) -> dict:
    """Load all JSON schemas in a directory

    :param schema_dir:
    :return:
    """
    result = {}
    for fpath in schema_dir.iterdir():
        name = fpath.stem
        with fpath.open(encoding="utf-8") as fp0:
            result[name] = json.load(fp0)
    #
    return result

def make_json_references(output_dir: Path, objects:dict[str:dict]) -> dict:
    """

    :param output_dir:
    :param objects:
    :return:
    """
    result = {}
    for fpath in output_dir.iterdir():
        os.remove(fpath)
    for name in objects:
        txt = json_reference_template.format(name=name)
        result[name] = txt
        fpath = output_dir / f"{name}Ref.json"
        with fpath.open("w", encoding="utf-8") as fp0:
            fp0.write(txt)
    #
    return result



if __name__ == "__main__":

    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(
        prog="generate_mxlims.py",
        formatter_class=RawTextHelpFormatter,
        prefix_chars="--",
        description="""
MXLIMS code generation. Assumes standard directory structure""",
    )

    parser.add_argument(
        "--dirname",
        metavar="dirname",
        default=None,
        help="Path to directory containing mxlims/ and docs/ subdirectory\n",
    )

    argsobj = parser.parse_args()
    options_dict = vars(argsobj)

    generate_mxlims(**options_dict)
