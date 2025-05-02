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
import re
from pathlib import Path
import subprocess
from subprocess import CalledProcessError
from typing import Optional, List


def generate_mxlims(dirname: Optional[str] = None) -> None :
    """
    Generate MXLIMS references JSON files and objects/ pydantic files

    :param dirname: path to mxlims working directory
    :return:
    """
    if dirname:
        mxlims_dir = Path(dirname)
    else:
        mxlims_dir = Path.cwd()

    object_dicts = extract_object_schemas(mxlims_dir / "mxlims" / "schemas")
    make_json_references(
        mxlims_dir / "mxlims" / "schemas" / "references", object_dicts
    )

    # clear and regenerate html docs
    for fp0 in (mxlims_dir/ "docs" / "html").iterdir():
        if fp0.is_file():
            os.remove(fp0)
    commands = [
        "generate-schema-doc",
        "--config-file",
        "docs/schemadoc_config.json",
        "mxlims/schemas",
        "docs/html",
    ]
    subprocess.run(commands, check=True, cwd=mxlims_dir)

    # Remove old pydantic files
    for subdir in ("data", "datatypes", "messages", "references", "objects", "core"):
        for fp0 in (mxlims_dir / "mxlims" / "pydantic" / subdir).iterdir():
            if fp0.is_file():
                os.remove(fp0)

    # generate Pydantic from schemas
    commands = [
        "datamodel-codegen",
        "--input-file-type",
        "jsonschema",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--base-class",
        "mxlims.pydantic.MxBaseModel.BaseModel",
        "--use-schema-description",
        "--use-double-quotes",
        "--disable-timestamp",
        "--use-default",
        "--target-python-version",
        "3.10",
        "--snake-case-field",
        "--use-exact-imports",
        "--capitalise-enum-members",
        "--use-title-as-name",
        "--use-one-literal-as-default",
        "--input",
        "mxlims/schemas",
        "--output",
        "mxlims/pydantic",
    ]
    try:
        proc = subprocess.run(
            commands, check=True, cwd=mxlims_dir, stderr=subprocess.STDOUT
        )
    except CalledProcessError:
        print(proc.stdout)
        raise

    # Generate final Pydantic objects
    objects_dir = mxlims_dir / "mxlims" / "pydantic" / "objects"
    for fpath in objects_dir.iterdir():
        os.remove(fpath)
    for classname, objdict in object_dicts.items():
        make_pydantic_object(objects_dir, objdict)


def extract_object_schemas(schema_dir: Path) -> dict:
    """Extract model specification schemas and convert to data for code generation

    The structure of the object-defining dict is, e.g. for MxProcessing
    (one link only given) :
    {
        "classname": "MxProcessing,
        "corename": "Job",
        "links": {
            "logistical_sample": {
                "linkname": "logistical_sample",
                "reversename": "jobs"
                "typenames": [
                    "Crystal","Pin","PinPosition","PlateWell","WellDrop","DropRegion",
                ],
                "basetypename": "LogisticalSample",
                "read_only": False,
                "cardinality": "single",
                "reverselink: dict() # The equivalent dictionary for the reverse link
            },
            ...
        }
    }
    reverse links (those not depending on uuid stored in this object)
    have no `reversename` element
    """

    data = {}
    for fpath in (schema_dir / "data").iterdir():
        dataname = fpath.stem
        with fpath.open(encoding="utf-8") as fp0:
            data[dataname] = json.load(fp0)

    result = {}
    for fpath in (schema_dir / "objects").iterdir():
        classname = fpath.stem
        with fpath.open(encoding="utf-8") as fp0:
            obj = json.load(fp0)
        result[classname] = objdict = {}
        objdict["links"] = {}

        # Read class-level info
        for dd1 in obj["allOf"]:
            # These are inherited data, specific and abstract superclass
            dataname = Path(dd1["$ref"]).stem
            dd2 = data[dataname]["properties"]
            type_record = dd2.get("mxlimsType")
            if type_record:
                objdict["classname"] = type_record["const"]
            else:
                # This must be the abstract base class
                objdict["corename"] = dd2["mxlimsBaseType"]["const"]

        # Read info for each link
        for linkref, linkjson in obj.get("properties", {}).items():
            linkname = camel_to_snake(linkref.rsplit("Ref", 1)[0])
            linkdict = objdict["links"][linkname] = {
                "linkname": linkname, "typenames":[]
            }
            if linkjson.get("type") == "array":
                # This is a to-many link
                linkdict["reversename"] = camel_to_snake(linkjson["reverseLinkName"])
                linkdict["read_only"] = linkjson.get("readOnly", False)
                linkdict["cardinality"] = "multiple"
                dd1 = linkjson["items"]
                if "$ref" in dd1:
                    # Single linked-to type
                    linkdict["typenames"].append(Path(dd1["$ref"]).stem.rsplit("Ref", 1)[0])
                elif "oneOf" in dd1:
                    # Multiple linked-to types
                    for dd2 in dd1["oneOf"]:
                        linkdict["typenames"].append(Path(dd2["$ref"]).stem.rsplit("Ref", 1)[0])
                else:
                    raise ValueError(
                        f"no 'oneOf' or '$ref' found in link {classname}.{linkname}"
                    )
            else:
                linkdict["cardinality"] = "single"
                for dd1 in linkjson["allOf"]:
                    if "$ref" in dd1:
                        # Single linked-to type
                        linkdict["typenames"].append(Path(dd1["$ref"]).stem.rsplit("Ref", 1)[0])
                    elif "oneOf" in dd1:
                        # Multiple linked-to types
                        for dd2 in dd1["oneOf"]:
                            linkdict["typenames"].append(Path(dd2["$ref"]).stem.rsplit("Ref", 1)[0])
                    else:
                        # This is the general properties of the link
                        linkdict["reversename"] = camel_to_snake(dd1["reverseLinkName"])
                        linkdict["read_only"] = dd1.get("readOnly", False)

    # Fill in records for reverse links
    for name, objdict in result.items():
        classname = objdict.get("classname")
        for linkname, linkdict in list(objdict["links"].items()):
            reversename = linkdict.get("reversename")
            if reversename:
                # This is a hardcoded link, add in reverse links
                revobjdict = {}
                for typename in linkdict["typenames"]:
                    revobjdict = result[typename]
                    revlinkdict = revobjdict["links"].get(reversename)
                    if revlinkdict:
                        revlinkdict["typenames"].append(classname)
                    else:
                        # NB all reverse links are multiple; there are no one-to-one links
                        revlinkdict = {
                            "linkname": reversename,
                            "read_only": True,
                            "typenames": [classname],
                            "basetypename": objdict["corename"],
                            "cardinality": "multiple"
                        }
                        revobjdict["links"][reversename] = revlinkdict
                        revlinkdict["reverselink"] = linkdict
                        linkdict["reverselink"] = revlinkdict
                # NB there will always have been one typename so revobjdict is non-empty
                linkdict["basetypename"] = revobjdict["corename"]
    #
    return result


def make_pydantic_object(output_dir: Path, objdict: dict) -> None:
    """ Generate and output final object pydantic file

    :param output_dir:
    :param objdict:
    :return:
    """
    all_types_set = set()
    for linkdict in objdict["links"].values():
        all_types_set.update(linkdict["typenames"])
    all_type_names = sorted(all_types_set)
    classname = objdict["classname"]
    corename = objdict["corename"]

    # Add top imports
    txtlist = [
        f"""# generated by mxlims/scripts
#  filename {classname}.py

from __future__ import annotations
from typing import Optional, Union
from ..core.{corename} import {corename}
from ..data.{corename}Data import {corename}Data
from ..data.{classname}Data import {classname}Data
""",
    ]

    # Add type-check imports
    if all_type_names and all_type_names != [objdict["classname"]]:
        # We have additional type to import
        # txtlist.append("if TYPE_CHECKING:\n")
        for typename in all_type_names:
            if typename != classname:
                txtlist.append(
                    f"from .{typename} import {typename}\n"
                )

    # Add class definition
    txtlist.append(f'''
class {classname}({classname}Data, {corename}Data, {corename}):
    """MXLIMS pydantic model class for {classname}
    """
    ''')

    # Add API properties for links
    for dummy, linkdict in sorted(objdict["links"].items()):
        cardinality = linkdict["cardinality"]
        if linkdict.get("reversename"):
            if cardinality == "single":
                txtlist.extend(
                    pydantic_single_link(classname=classname, linkdict=linkdict)
                )
            else:
                txtlist.extend(
                    pydantic_multiple_link(classname=classname, linkdict=linkdict)
                )
        else:
            if cardinality == "single":
                raise ValueError(
                    "Unsupported reverse single link found for {classname}.{linkname}"
                )
            else:
                txtlist.extend(pydantic_multiple_reverse_link(
                    classname=classname, linkdict=linkdict)
                )
    # store result
    fpath = output_dir / f"{classname}.py"
    with fpath.open("w", encoding="utf-8") as fp0:
        fp0.writelines(txtlist)

def pydantic_single_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    basetypename = linkdict["basetypename"]
    typenames = linkdict["typenames"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"
    result = [f'''
    @property
    def {linkname}(self) -> Optional[{linktype}]:
        """getter for {classname}.{linkname}"""
        return self.objects_by_id["{basetypename}"].get(self.{linkname}_id)
    '''
    ]
    if not linkdict.get("read_only"):
        result.append(f'''
    @{linkname}.setter
    def {linkname}(self, value: Optional[{linktype}]):
        """setter for {classname}.{linkname}"""
        if value:
            if not isinstance(value, {linktype}):
                raise ValueError(
                    "{linkname} must be of type {linktype}"
                )
            self.{linkname}_id = value.uuid
        else:
            self.{linkname}_id = None
'''
        )
    #
    return result

def pydantic_multiple_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    basetypename = linkdict["basetypename"]
    typenames = linkdict["typenames"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"

    result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """getter for {classname}.{linkname} list"""
        result = []
        for uid in self.{linkname}_ids:
            obj = self.objects_by_id["{basetypename}"].get(uid)
            if obj:
                result.append(obj)
        return result
    '''
    ]

    if not linkdict.get("read_only"):
        result.append(f'''
    @{linkname}.setter
    def {linkname}(self, value: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
        uids = []
        for obj in value:
            if isinstance(obj, {linktype}):
                uids.append(obj.uuid)
            else:
                raise ValueError("%s is not of type {linktype}" % value)
        self.{linkname}_ids = uids

    def append_{linkname}(self, value: {linktype}):
        """append to {classname}.{linkname} list"""
        if isinstance(value, {linktype}):
            uid = value.uuid
            if uid in self.{linkname}_ids:
                raise ValueError("%s is already in {classname}.{linkname}" % value)
            else:
                self.{linkname}_ids.append(uid)
        else:
            raise ValueError("%s is not of type {linktype}" % value)

    def remove_{linkname}(self, value: {linktype}):
        """remove from {classname}.{linkname} list"""
        if isinstance(value, {linktype}):
            uid = value.uuid
            if uid in self.{linkname}_ids:
                self.{linkname}_ids.remove(uid)
            else:
                raise ValueError("Input %s not found" % value)
        else:
            raise ValueError("%s is not of type {linktype}" % value)
'''
        )
    #
    return result


def pydantic_multiple_reverse_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    basetypename = linkdict["basetypename"]
    typenames = linkdict["typenames"]
    reverselink = linkdict["reverselink"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"

    if reverselink["cardinality"] == "single":
        result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """getter for {classname}.{linkname} list"""
        uid = self.uuid
        result = []
        for obj in self.objects_by_id["{basetypename}"]:
            if uid == obj.{reverselink["linkname"]}_id:
                result.append(obj)
        return result
    '''
        ]
    else:
        result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """getter for {classname}.{linkname} list"""
        uid = self.uuid
        result = []
        for obj in self.objects_by_id["{basetypename}"]:
            if uid in obj.{reverselink["linkname"]}_ids:
                result.append(obj)
        return result
    '''
        ]

    if not linkdict.get("read_only"):
        if reverselink["cardinality"] == "single":
            result.append(f'''
    @{linkname}.setter
    def {linkname}(self, value: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
        myuid = self.uuid
        for obj in value:
            if isinstance(obj, {linktype}):
                obj.{reverselink["linkname"]}_id = myuid
            else:
                raise ValueError("%s is not of type {linktype}" % value)

    def append_{linkname}(self, value: {linktype}):
        """append to {classname}.{linkname} list"""
        myuid = self.uuid
        if isinstance(value, {linktype}):
            if value.{reverselink["linkname"]}_id == myuid:
                raise ValueError("%s is already in {classname}.{linkname}" % value)
            else:
                value.{reverselink["linkname"]}_id = myuid
        else:
            raise ValueError("%s is not of type {linktype}" % value)

    def remove_{linkname}(self, value: {linktype}):
        """remove from {classname}.{linkname} list"""
        if isinstance(value, {linktype}):
            if value.{reverselink["linkname"]}_id != self.uuid:
                raise ValueError("%s is not in {classname}.{linkname}" % value)
            else:
                value.{reverselink["linkname"]}_id = None
        else:
            raise ValueError("%s is not of type {linktype}" % value)
    '''
            )
        else:
            # reverse link is multiple
            result.append(f'''
    @{linkname}.setter
    def {linkname}(self, value: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
        myuid = self.uuid
        for obj in self.objects_by_id["{basetypename}"]:
            if obj in value:
                if isinstance(obj, {linktype}):
                    if myuid not in obj.{reverselink["linkname"]}_ids
                        obj.{reverselink["linkname"]}_ids.append(myuid)
                else:
                    raise ValueError("%s is not of type {linktype}" % value)
            elif isinstance(obj, {linktype}) and myuid in obj.{reverselink["linkname"]}_ids:
                obj.{reverselink["linkname"]}_ids.remove(myuid)

    def append_{linkname}(self, value: {linktype}):
        """append to {classname}.{linkname} list"""
        myuid = self.uuid
        if isinstance(value, {linktype}):
            if myuid in value.{reverselink["linkname"]}_id:
                raise ValueError("%s is already in {classname}.{linkname}" % value)
            else:
                value.{reverselink["linkname"]}_ids.append(myuid)
        else:
            raise ValueError("%s is not of type {linktype}" % value)

    def remove_{linkname}(self, value: {linktype}):
        """remove from {classname}.{linkname} list"""
        myuid = self.uuid
        if isinstance(value, {linktype}):
            if myuid in value.{reverselink["linkname"]}_ids:
                value.{reverselink["linkname"]}_ids.remove(myuid)
            else:
                raise ValueError("%s is not in {classname}.{linkname}" % value)
        else:
            raise ValueError("%s is not of type {linktype}" % value)
    '''
            )
    #
    return result

def make_json_references(output_dir: Path, object_dicts:dict[str:dict]):
    """

    :param output_dir:
    :param object_dicts:
    :return:
    """

    jsonref_file_template = """{{
        "$schema": "https://json-schema.org/draft-07/schema",
        "description": "Reference to {classname}",
        "title": "{classname}Ref",
        "type": "object",
        "properties": {{
            "mxlimsType": {{
                "description": "The type of the MXLIMS object referred to.",
                "title": "MxlimsType",
                "type": "string",
                "const": "{classname}"
            }},
            "$ref": {{
                "description": "JSON reference to object in std. message, using uuid-based links.",
                "title": "JSONreference",
                "type": "string",
                "pattern": "^/{classname}/[a-fA-F0-9]{{8}}-?[a-fA-F0-9]{{4}}-?[1-5][a-fA-F0-9]{{3}}-?[89abAB][a-fA-F0-9]{{3}}-?[a-fA-F0-9]{{12}}$"
            }}
        }},
        "required": [
            "$ref"
        ],
        "additionalProperties": false
    }}
    """

    for fpath in output_dir.iterdir():
        os.remove(fpath)
    for classname in object_dicts:
        txt = jsonref_file_template.format(classname=classname)
        fpath = output_dir / f"{classname}Ref.json"
        with fpath.open("w", encoding="utf-8") as fp0:
            fp0.write(txt)

def camel_to_snake(name: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()

def snake_to_camel(name:str) -> str:
    return "".join(txt.capitalize() for txt in name.split("_"))


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
