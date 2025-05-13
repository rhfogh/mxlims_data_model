#! /usr/bin/env python
# encoding: utf-8
""" Utility code for MXLIMS model

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

from pathlib import Path
import re
from ruamel.yaml import YAML

yaml = YAML(typ="safe", pure=True)
# The following are not needed for load, but define the default style.
yaml.default_flow_style = False
yaml.indent(mapping=4, sequence=4, offset=2)


with (Path(__file__).parent / "link_specification.yaml").open(encoding="utf-8") as fp0:
    LINK_SPECIFICATION = yaml.load(fp0)


def camel_to_snake(name: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()

def snake_to_camel(name:str) -> str:
    ll0 =  name.split("_")
    if len(ll0) < 2:
        return name
    return ll0[0] + "".join(txt.capitalize() for txt in ll0[1:])


def to_export_json(message_dict: dict) -> None:
    """Convert schema-compliant JSON from ID-type links to ref-type links

    Conversion is done in-place"""
    import json
    Path("/home/rhfogh/tmp/messags.json").write_text(json.dumps(message_dict, indent=4))
    obj_by_uuid = {}
    for dd1 in message_dict.values():
        if dd1:
            for obj in dd1.values():
                obj_by_uuid[str(obj["uuid"])]= obj
    for tag, objdict in list(message_dict.items()):
        if not objdict:
            message_dict.pop(tag)
        refdict = LINK_SPECIFICATION.get(tag)
        for uid,obj in objdict.items():
            for linkdict in refdict["links"].values():
                link_id_name_orig = linkdict.get("link_id_name")
                if link_id_name_orig:
                    link_id_name = snake_to_camel(link_id_name_orig)
                    link_uid = obj.pop(link_id_name, ())
                    # This is a link with a foreign key
                    if linkdict["cardinality"] == "single":
                        if link_uid:
                            link_target = obj_by_uuid.get(link_uid)
                            if link_target:
                                # The linked-to object is in the message
                                mxlims_type = link_target["mxlimsType"]
                                obj[linkdict["link_ref_name"]] = {
                                    "mxlimsType": mxlims_type,
                                    "$ref": f"/{mxlims_type}/{link_uid}"
                                }
                            else:
                                base_type = linkdict["basetypename"]
                                if base_type in message_dict:
                                    # Object not in message.
                                    # Put Stub link, if allowed
                                    obj[linkdict["link_ref_name"]] = {
                                        "mxlimsBaseType": base_type,
                                        "$ref": f"/{base_type}/{link_uid}"
                                    }
                                    # And add stub to the message
                                    message_dict[base_type][str(link_uid)] = {
                                        "mxlimsBaseType": base_type,
                                        "uuid": str(link_uid)
                                    }
                    else:
                        # Multiple link - link_uid is a list
                        if link_uid:
                            obj[linkdict["link_ref_name"]] = reflist = []
                            for luid in link_uid:
                                link_target = obj_by_uuid.get(luid)
                                if link_target:
                                    # The linked-to object is in the message
                                    mxlims_type = link_target["mxlimsType"]
                                    newref = {
                                        "mxlimsType": mxlims_type,
                                        "$ref": f"/{mxlims_type}/{luid}"
                                    }
                                else:
                                    base_type = linkdict["basetypename"]
                                    if base_type in message_dict:
                                        # Object not in message.
                                        # Put Stub link, if allowed
                                        newref = {
                                            "mxlimsBaseType": base_type,
                                            "$ref": f"/{base_type}/{luid}"
                                        }
                                        # And add stub to the message
                                        message_dict[base_type][str(luid)] = {
                                            "mxlimsBaseType": base_type,
                                            "uuid": str(luid)
                                        }
                                reflist.append(newref)

def to_import_json(message_dict: dict) -> None:
    """Convert JSON read from schema-compliant JSON files to pydantic-compliant

    Conversion is done in-place

    :param message_dict: schema-compliant JSON message
    :return:
    """
    for tag, objdict in list(message_dict.items()):
        refdict = LINK_SPECIFICATION.get(tag)
        for obj in objdict.values():
            for linkdict in refdict["links"].values():
                link_id_name_orig = linkdict.get("link_id_name")
                link_ref_name = linkdict.get("link_ref_name")
                if link_id_name_orig:
                    # This is a link with a foreign key
                    link_id_name = snake_to_camel(link_id_name_orig)
                    data = obj.pop(link_ref_name, None)
                    if data:
                        if linkdict["cardinality"] == "single":
                            mxlims_type = data["mxlimsType"]
                            uidstr = data["$ref"].split("/")[-1]
                            obj[link_id_name] = (
                                message_dict[mxlims_type][uidstr]["uuid"]
                            )
                        else:
                            uids = obj[link_id_name] = []
                            for ddref in data:
                                mxlims_type = ddref["mxlimsType"]
                                uidstr = ddref["$ref"].split("/")[-1]
                                uids.append(
                                    message_dict[mxlims_type][uidstr]["uuid"]
                                )
