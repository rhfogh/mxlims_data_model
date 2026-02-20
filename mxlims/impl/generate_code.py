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

__copyright__ = """ Copyright © 2024 -  2025 MXLIMS collaboration."""
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
    fpath = mxlims_dir / "mxlims" / "impl" / "link_specification.yaml"
    with fpath.open("w", encoding="utf-8") as fp0:
        # We need yaml because of circular references
        yaml.dump(object_dicts, fp0)

    # import pprint
    # pprint.pprint(object_dicts)
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
    for subdir in ("data", "datatypes", "messages", "references"):
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
        "mxlims.impl.MxlimsBase.BaseModel",
        "--use-schema-description",
        "--use-double-quotes",
        "--disable-timestamp",
        "--use-default",
        "--target-python-version",
        "3.10",
        "--snake-case-field",
        "--output-datetime-class",
        "AwareDatetime",
        "--use-exact-imports",
        "--capitalise-enum-members",
        "--use-title-as-name",
        "--use-one-literal-as-default",
        "--use-non-positive-negative-number-constrained-types",
        "--collapse-root-models",
        "--input",
        "mxlims/schemas",
        "--output",
        "mxlims/pydantic",
    ]
    try:
        subprocess.run(
            commands,
            check=True,
            cwd=mxlims_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except CalledProcessError as exc:
        print(exc.stdout.decode())
        raise

    # # Temporary HACK
    # # TBD replace with fully generated core classes
    # jobfile = mxlims_dir / "mxlims" / "pydantic" / "core" / "Job.py"
    # text = jobfile.read_text()
    # text = text.replace("...", "default_factory=list")
    # jobfile.write_text(text)

    # Generate final Pydantic objects
    pydantic_dir = mxlims_dir / "mxlims" / "pydantic"
    for fp0 in (pydantic_dir / "objects").iterdir():
        if fp0.is_file():
            os.remove(fp0)
    for classname, objdict in object_dicts.items():
        make_pydantic_object(pydantic_dir, objdict)

    # Generate MXLIMS Message classes
    generate_message_classes(mxlims_dir)

    # Post-process pydantic classes - first st up to replace AnyUrl by HttpUrl
    for fpath in pydantic_dir.rglob("*.py"):
        post_process_pydantic_file(fpath)

    # Regenerate field name mappings
    generate_fields(mxlims_dir)

def post_process_pydantic_file(fpath: Path):
        text = open(fpath).read()
        if "AnyUrl" in text:
            text = text.replace("AnyUrl", "HttpUrl")
            open(fpath, "w").write(text)

def generate_message_classes(mxlims_dir: Path) -> None:
    """ Adjust and re-write MxlimsMessage classes

    :param mxlims_dir:
    :return:
    """
    input_dir = mxlims_dir / "mxlims" / "pydantic" / "messages"
    for fp0 in input_dir.iterdir():
        if fp0.is_file():
            classname = fp0.stem
            if classname == "__init__":
                continue
            text = fp0.read_text()
            text = text.replace("BaseModel", "BaseMessage")
            text = text.replace("None,", "default_factory=dict,")
            fp0.write_text(text)

def extract_object_schemas(schema_dir: Path) -> dict:
    """Extract model specification schemas and convert to data for code generation

    See .../mxlims_data_model/mlxlims/pydantic/linl_specification.yaml
    for the structure of the data produced here.

    reverse links (those not depending on uuid stored in this object)
    have no `reversename` element
    The `rolename` used in the implementation is the forward link name
    """

    data = {}
    for fpath in (schema_dir / "data").iterdir():
        dataname = fpath.stem
        print ('Loading file:', fpath)
        with fpath.open(encoding="utf-8") as fp0:
            data[dataname] = json.load(fp0)

    result = {}
    for fpath in (schema_dir / "objects").iterdir():
        classname = fpath.stem
        with fpath.open(encoding="utf-8") as fp0:
            obj = json.load(fp0)

        result[classname] = objdict = {}
        objdict["links"] = {}

        if obj.get("unevaluatedProperties") == False:
            objdict["noExtraProperties"] = True

        # Read class-level info
        for dd1 in obj["allOf"]:
            # These are inherited data, specific and abstract superclass
            reference = dd1["$ref"]
            if "/data/" in reference:
                if not reference.endswith("Data.json"):
                    raise ValueError("/data/ json file names must end with 'Data.json'")
                dataname = Path(reference).stem
                dd2 = data[dataname]
                if dataname[:-4] in CORETYPES:
                    objdict["corename"] = dataname[:-4]
                else:
                    objdict["classname"] = obj["properties"]["mxlimsType"]["const"]
        if not objdict.get("classname"):
            # This is one of the core objects
            objdict["classname"] = objdict["corename"]

        # Read info for each link
        for linkref, linkjson in obj.get("properties", {}).items():
            linkname = camel_to_snake(linkref.rsplit("Ref", 1)[0])
            linkdict = {
                "linkname": linkname, "typenames":[], "link_ref_name": linkref
            }
            if linkjson.get("type") == "array":
                # This is a to-many link
                linkdict["reversename"] = camel_to_snake(linkjson["reverseLinkName"])
                linkdict["read_only"] = linkjson.get("readOnly", False)
                linkdict["cardinality"] = "multiple"
                linkdict["link_id_name"] = linkname + "_ids"
                dd1 = linkjson["items"]
                if "$ref" in dd1:
                    # Single linked-to type
                    typename = Path(dd1["$ref"]).stem.rsplit("Ref", 1)[0]
                    linkdict["typenames"].append(typename)
                elif "oneOf" in dd1:
                    # Multiple linked-to types
                    for dd2 in dd1["oneOf"]:
                        typename = Path(dd2["$ref"]).stem.rsplit("Ref", 1)[0]
                        if typename not in CORETYPES:
                            linkdict["typenames"].append(typename)
                else:
                    raise ValueError(
                        f"no 'oneOf' or '$ref' found in link {classname}.{linkname}"
                    )
                objdict["links"][linkname] = linkdict
            elif linkjson.get("type") is None:
                linkdict["cardinality"] = "single"
                linkdict["link_id_name"] = linkname + "_id"
                for dd1 in linkjson["allOf"]:
                    if "$ref" in dd1:
                        # Single linked-to type
                        linkdict["typenames"].append(Path(dd1["$ref"]).stem.rsplit("Ref", 1)[0])
                    elif "oneOf" in dd1:
                        # Multiple linked-to types
                        for dd2 in dd1["oneOf"]:
                            typename = Path(dd2["$ref"]).stem.rsplit("Ref", 1)[0]
                            if typename not in CORETYPES:
                                linkdict["typenames"].append(typename)
                    else:
                        # This is the general properties of the link
                        linkdict["reversename"] = camel_to_snake(dd1["reverseLinkName"])
                        linkdict["read_only"] = dd1.get("readOnly", False)
                objdict["links"][linkname] = linkdict

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
                            "typenames": [classname],
                            "basetypename": objdict["corename"],
                            "cardinality": "multiple"
                        }
                        if linkdict.get("read_only"):
                            revlinkdict["read_only"] = True
                        revobjdict["links"][reversename] = revlinkdict
                    revlinkdict["reverselink"] = linkdict
                    linkdict["reverselink"] = revlinkdict
                # NB there will always have been one typename so revobjdict is non-empty
                linkdict["basetypename"] = revobjdict["corename"]
    #
    return result


def make_pydantic_object(pydantic_dir: Path, objdict: dict) -> None:
    """ Generate and output final object pydantic file

    :param pydantic_dir_dir:
    :param objdict:
    :return:
    """

    if objdict.get("noExtraProperties"):
        config_dict_str = "ConfigDict, "
    else:
        config_dict_str = ""

    all_types_set = set()
    for linkdict in objdict["links"].values():
        all_types_set.update(linkdict["typenames"])
    all_type_names = sorted(all_types_set)
    classname = objdict["classname"]
    corename = objdict["corename"]

    if classname == corename:
        if corename == "Dataset":
            validator_str = ", model_validator"
        else:
            validator_str = ""
        txtlist = [
        f"""# generated by mxlims/impl/generate_code.py
#  filename {classname}.py

from __future__ import annotations
from pydantic import {config_dict_str}Field{validator_str}
from typing import List, Literal, Optional, TYPE_CHECKING
from uuid import UUID, uuid1
from mxlims.core.MxlimsObject import MxlimsObject
from ..data.{classname}Data import {classname}Data
""",
        ]
        # Add type-check imports
        if all_type_names and all_type_names != [objdict["classname"]]:
            # We have additional type to import
            txtlist.append("if TYPE_CHECKING:\n")
            for typename in all_type_names:
                if typename != classname:
                    txtlist.append(
                        f"    from .{typename} import {typename}\n"
                    )
            if classname == "Dataset":
                # HACK, used for sourceId/derivedFromId validator
                txtlist.append("    from typing_extensions import Self\n")

        txtlist.append(f'''
class {classname}({classname}Data, MxlimsObject):
    """MXLIMS pydantic model class for {classname}
    """
'''
    )
        if objdict.get("noExtraProperties"):
            txtlist.append(f'''
    model_config = ConfigDict(
        extra="forbid",
    )
        ''')

        txtlist.append(f'''
    mxlims_base_type: Literal["{classname}"] = Field(
        "{classname}",
        alias="mxlimsBaseType",
        description="The abstract (super)type of MXLIMS object.",
        title="MxlimsBaseType",
        exclude=True,
        frozen=True
    )
    mxlims_type: str = Field(
        "{classname}",
        alias="mxlimsType",
        description="The type of MXLIMS object.",
        title="MxlimsType",
        frozen=True,
    )
    uuid: Optional[UUID] = Field(
        default_factory=uuid1,
        description="Permanent unique identifier string",
        title="Uuid",
        frozen=True
    )''')
        # Add _id fields from autogenerated code
        fp1 = pydantic_dir / "core" / f"{classname}.py"
        text = fp1.read_text(encoding="utf-8")
        text1 = text.split('"""')[-1]
        lines = text1.splitlines()
        for ii in range(len(lines)):
            if "List[UUID]" in lines[ii]:
                lines[ii+1] = lines[ii+1].replace("None", "default_factory=list")
        txtlist.append("\n".join(lines))
        fp1.unlink()

        # Add API properties for links
        for dummy, linkdict in sorted(objdict["links"].items()):
            cardinality = linkdict["cardinality"]
            if linkdict.get("link_id_name"):
                if cardinality == "single":
                    txtlist.extend(
                        pydantic_dummy_single_link(classname=classname, linkdict=linkdict)
                    )
                else:
                    txtlist.extend(
                        pydantic_dummy_multiple_link(classname=classname, linkdict=linkdict)
                    )
            else:
                if cardinality == "single":
                    raise ValueError(
                        "Unsupported reverse single link found for {classname}.{linkname}"
                    )
                else:
                    txtlist.extend(pydantic_dummy_multiple_link(
                        classname=classname, linkdict=linkdict)
                    )
        if corename == "Dataset":
            # NBNB HACK
            # This introduces teh constraint that a DAtaset cannot have both sourceId
            # and derivedFromId at eth same time
            # This is set separately in the JSONSchema specification, but because
            # of limitations in datamodel-code-generator it is not possible to
            # convert this limit to Pydantic (if-then-else is ignored by the generator,
            # and anyOf, oneOf etc. trigger undesirable changes in the Pydantic code
            txtlist.append(
"""
    @model_validator(mode='after')
    def source_and_derivedFrom_are_mutually_exclusive(self) -> Self:
        if self.source_id is not None and self.derived_from_id is not None:
            raise ValueError("source and derivedFrom are mutually exclusive")
        return self
"""
            )

    else:

        # Add top imports
        txtlist = [
        f"""# generated by mxlims/impl/generate_code.py
#  filename {classname}.py

from __future__ import annotations
from pydantic import {config_dict_str}Field
from typing import Any, Literal, Optional, Union, TYPE_CHECKING
from ..objects.{corename} import {corename}
from ..data.{classname}Data import {classname}Data
""",
        ]

        # Add type-check imports
        if all_type_names and all_type_names != [objdict["classname"]]:
            # We have additional type to import
            txtlist.append("if TYPE_CHECKING:\n")
            for typename in all_type_names:
                if typename != classname:
                    txtlist.append(
                        f"    from .{typename} import {typename}\n"
                    )

        # Add class definition
        txtlist.append(f'''
class {classname}({classname}Data, {corename}):
    """MXLIMS pydantic model class for {classname}
    """
        
    mxlims_type: Literal["{classname}"] = Field(
        "{classname}",
        alias="mxlimsType",
        description="The type of MXLIMS object.",
        title="MxlimsType",
        frozen=True,
    )
    ''')
        if objdict.get("noExtraProperties"):
            txtlist.append(f'''
    model_config = ConfigDict(
        extra="forbid",
    )
        ''')

        # Add API properties for links
        for dummy, linkdict in sorted(objdict["links"].items()):
            cardinality = linkdict["cardinality"]
            if linkdict.get("link_id_name"):
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
    fpath = pydantic_dir / "objects" / f"{classname}.py"
    with fpath.open("w", encoding="utf-8") as fp0:
        fp0.writelines(txtlist)

def pydantic_single_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    link_id_name = linkdict["link_id_name"]
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
        return self._get_link_n1("{basetypename}", "{link_id_name}")
'''
    ]
    if not linkdict.get("read_only"):
        result.append(
            f'''
    @{linkname}.setter
    def {linkname}(self, value: Optional[{linktype}]):
        """setter for {classname}.{linkname}"""
'''
        )
        for typename in typenames:
            result.append(f"        from .{typename} import {typename}\n")
        result.append(
            f'''
        if value is None or isinstance(value, {linktype}):
            self._set_link_n1("{basetypename}", "{link_id_name}", value)
        else:
            raise ValueError("{linkname} must be of type {linktype} or None")
'''
        )
    #
    return result
def pydantic_dummy_single_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    typenames = linkdict["typenames"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"
    result = [f'''
    @property
    def {linkname}(self) -> Optional[{linktype}]:
        """Abstract superclass - dummy getter for {classname}.{linkname}"""
        return None
'''
    ]
    #
    return result

def pydantic_multiple_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    link_id_name = linkdict["link_id_name"]
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
        return self._get_link_nn("{basetypename}", "{link_id_name}")
'''
    ]

    if not linkdict.get("read_only"):
        result.append(f'''
    @{linkname}.setter
    def {linkname}(self, values: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
'''
        )
        for typename in typenames:
            result.append(f"        from .{typename} import {typename}\n")
        result.append(
            f'''
        for obj in values:
            if not isinstance(obj, {linktype}):
                raise ValueError("%s is not of type {linktype}" % obj)
        self._set_link_nn("{basetypename}", "{link_id_name}", values)

    def append_{linkname}(self, value: {linktype}):
        """append to {classname}.{linkname} list"""
'''
        )
        for typename in typenames:
            result.append(f"        from .{typename} import {typename}\n")
        result.append(
            f'''
        if isinstance(value, {linktype}):
            self._append_link_nn("{link_id_name}", value)
        else:
            raise ValueError("%s is not of type {linktype}" % value)

    def remove_{linkname}(self, value: {linktype}):
        """remove from {classname}.{linkname} list"""
'''
        )
        for typename in typenames:
            result.append(f"        from .{typename} import {typename}\n")
        result.append(
            f'''
        if isinstance(value, {linktype}):
            self._remove_link_nn("{link_id_name}", value)
        else:
            raise ValueError("%s is not of type {linktype}" % value)
'''
        )
    #
    return result

def pydantic_dummy_multiple_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    typenames = linkdict["typenames"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"

    result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """Abstract superclass - dummy getter for {classname}.{linkname} list"""
        return []
'''
    ]
    #
    return result


def pydantic_multiple_reverse_link(classname: str, linkdict:dict) -> List[str]:
    linkname = linkdict["linkname"]
    basetypename = linkdict["basetypename"]
    typenames = linkdict["typenames"]
    reverselink = linkdict["reverselink"]
    reverse_id_name = reverselink["link_id_name"]
    reversename = reverselink["linkname"]
    if len(typenames) == 1:
        linktype = typenames[0]
    else:
        linktype = f"Union[{', '.join(sorted(typenames))}]"

    if reverselink["cardinality"] == "single":
        result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """getter for {classname}.{linkname} list"""
        return self._get_link_1n("{basetypename}", "{reverse_id_name}")
'''
        ]
    else:
        result = [f'''
    @property
    def {linkname}(self) -> list[{linktype}]:
        """getter for {classname}.{linkname} list"""
        return self._get_link_nn_rev("{basetypename}", "{reverse_id_name}")
'''
        ]

    if not linkdict.get("read_only"):
        if reverselink["cardinality"] == "single":
            result.append(
                f'''
    @{linkname}.setter
    def {linkname}(self, values: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
'''
            )
            for typename in typenames:
                result.append(f"        from .{typename} import {typename}\n")
            result.append(
            f'''
        for obj in values:
            if not isinstance(obj, {linktype}):
                raise ValueError("%s is not of type {linktype}" % obj)
        self._set_link_1n_rev("{basetypename}", "{reverse_id_name}", values)
'''
            )
        else:
            # reverse link is multiple
            result.append(
                f'''
    @{linkname}.setter
    def {linkname}(self, values: list[{linktype}]):
        """setter for {classname}.{linkname} list"""
'''
            )
            for typename in typenames:
                result.append(f"        from .{typename} import {typename}\n")
            result.append(
                f'''
        for obj in values:
            if not isinstance(obj, {linktype}):
                raise ValueError("%s is not of type {linktype}" % obj)
        self._set_link_nn_rev("{basetypename}", "{reverse_id_name}", values)
'''
            )
            result.append(
                f'''
    def append_{linkname}(self, value: {linktype}):
        """append to {classname}.{linkname} list"""
        value.append_{reversename}(self)

    def remove_{linkname}(self, value: {linktype}):
        """remove from {classname}.{linkname} list"""
        value.remove_{reversename}(self)
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
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mxlims.org/schemas/references/{classname}Ref.json",
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
            "pattern": "^#/{classname}/{classname}[1-9][0-9]*$"
        }}
    }},
    "required": [
        "$ref"
    ],
    "additionalProperties": false
}}
    """

    for fp0 in output_dir.iterdir():
        if fp0.is_file():
            os.remove(fp0)
    for classname in object_dicts:
        (output_dir / f"{classname}Ref.json").write_text(
            jsonref_file_template.format(classname=classname),
            encoding="utf-8"
        )


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
