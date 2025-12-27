# encoding: utf-8
""" Python implementation base classes for MXLIMS model

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
from __future__ import annotations

__copyright__ = """ Copyright © 2024 -  2025 MXLIMS collaboration."""
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

import enum
import json
import re
import uuid
from pathlib import Path
from typing import ClassVar, List, Optional, Sequence, TYPE_CHECKING

from pydantic import BaseModel as PydanticBaseModel
from ruamel.yaml import YAML

if TYPE_CHECKING:
    from .Dataset import Dataset
    from Job import Job
    from .LogisticalSample import LogisticalSample
    from .Sample import Sample

yaml = YAML(typ="safe", pure=True)
# The following are not needed for load, but define the default style.
yaml.default_flow_style = False
yaml.indent(mapping=4, sequence=4, offset=2)

# Names of core *(basic abstract) classes
CORETYPES = ("Job", "Dataset", "LogisticalSample", "Sample")

with (Path(__file__).parent / "link_specification.yaml").open(encoding="utf-8") as fp0:
    LINK_SPECIFICATION = yaml.load(fp0)

class UuidClashMode(enum.Enum):
    """Enumeration for how to handle uuid clashes between input and existing objects

    Alternatives are:

    - update_old: all attributes present on the new object are set on the old
    - reject_new: The new object is ignored; links to it are attached to the old object
    - error: Raise ValueError on uuid clashes
    """
    update_old = "update_old"
    reject_new = "reject_new"
    error = "error"

class BaseModel(PydanticBaseModel):

    class Config:
        populate_by_name = True
        extra = "forbid"
        use_enum_values = True
        validation_error_cause = True

class MxlimsImplementation:

    # Class-level container for implementation of access-object-by-id
    _objects_by_id: ClassVar[dict] = {
        "Dataset": dict(),
        "Job": dict(),
        "Sample": dict(),
        "LogisticalSample": dict(),
    }

    def __init__(self) -> None:
        obj_by_id = self._objects_by_id[self.mxlims_base_type]
        myuid = self.uuid
        if myuid in obj_by_id:
            raise ValueError(
                f"{self.mxlims_base_type} with uuid '{myuid}' already exists"
            )
        else:
            obj_by_id[myuid] = self

    @classmethod
    def get_all_jobs(cls) -> list[Job]:
        """Get list of all Jobs"""
        return list(cls._objects_by_id["Job"].values())

    @classmethod
    def get_all_datasets(cls) -> list[Dataset]:
        """Get list of all Datasets"""
        return list(cls._objects_by_id["Dataset"].values())

    @classmethod
    def get_all_samples(cls) -> list[Sample]:
        """Get list of all Samples"""
        return list(cls._objects_by_id["Sample"].values())

    @classmethod
    def get_all_logistical_samples(cls) -> list[LogisticalSample]:
        """Get list of all Jobs"""
        return list(cls._objects_by_id["LogisticalSample"].values())

    @classmethod
    def get_object_by_uuid(
        cls,
        uuid: str,
        basetypename: Optional[str] = None,
    ) -> Optional["MxlimsImplementation"]:
        """
        Get MXLIMS object from basetypename and (foreign key) uuid

        :param basetypename:
        :param uuid:
        :return:
        """
        if basetypename is None:
            for dd1 in  cls._objects_by_id.values():
                result = dd1.get(uuid)
                if result  is not None:
                    break
        else:
            result = cls._objects_by_id[basetypename].get(uuid)
        return result

    def _get_link_n1(
            self,
            basetypename: str,
            id_field_name: str
    ) -> Optional["MxlimsImplementation"]:
        """Getter for n..1 forward link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name: Name of (forward-direction) link
        :return MxlimsImplementation: Linked-to object
        """
        return self._objects_by_id[basetypename].get(getattr(self, id_field_name))

    def _set_link_n1(
        self,
        basetypename: str,
        id_field_name: str,
        value: Optional["MxlimsImplementation"]
    ):
        """Setter for n..1 forward link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name:
        :param value:
        :return: None
        """
        if value:
            setattr(self, id_field_name, value.uuid)
        else:
            setattr(self, id_field_name, None)

    def _get_link_nn(
        self,
        basetypename: str,
        id_field_name: str
    ) -> List["MxlimsImplementation"]:
        """Getter for n..n forward link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name:
        :return:
        """
        result = []
        for uid in getattr(self, id_field_name):
            obj = self._objects_by_id[basetypename].get(uid)
            if obj:
                result.append(obj)
        return result

    def _set_link_nn(
        self,
        basetypename: str,
        id_field_name: str,
        values: Sequence["MxlimsImplementation"]
    ):
        """Setter for n..n forward link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name:
        :param values:
        :return:
        """
        setattr(self, id_field_name, list(obj.uuid for obj in values))

    def _append_link_nn(self, id_field_name: str, value: "MxlimsImplementation"):
        """Append for n..n forward link

        :param id_field_name:
        :param value:
        :return:
        """
        uid = value.uuid
        uids = getattr(self, id_field_name)
        if uid in uids:
            raise ValueError("Cannot append - object is already in link")
        else:
            uids.append(uid)

    def _remove_link_nn(self, id_field_name: str, value: "MxlimsImplementation"):
        """Remove for n..n forward link

        :param id_field_name:
        :param value:
        :return:
        """
        uid = value.uuid
        uids = getattr(self, id_field_name)
        if uid in uids:
            uids.remove(uid)
        else:
            raise ValueError("Cannot remove - object not found")

    def _get_link_1n(
            self, basetypename: str, id_field_name: str
    ) -> List["MxlimsImplementation"]:
        """Getter for 1..n reverse link

        :param basetypename:
        :param id_field_name:
        :return:
        """
        myuid = self.uuid
        result = list(
            obj
            for obj in self._objects_by_id[basetypename].values()
            if myuid == getattr(obj, id_field_name)
        )
        return result

    def _get_link_nn_rev(
        self, basetypename: str, id_field_name: str
    ) -> List["MxlimsImplementation"]:
        """Getter for n..n reverse link

        :param basetypename:
        :param id_field_name:
        :return:
        """
        myuid = self.uuid
        result = list(
            obj
            for obj in self._objects_by_id[basetypename].values()
            if myuid in getattr(obj, id_field_name)
        )
        return result

    def _set_link_1n_rev(
        self,
        basetypename: str,
        id_field_name: str,
        values: Sequence["MxlimsImplementation"]
    ):
        """Setter for 1..n reverse link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name:
        :param values:
        :return:
        """
        myuid = self.uuid
        uids = list(obj.uuid for obj in values)
        for obj in self._objects_by_id[basetypename].values():
            if getattr(obj, id_field_name) == myuid and obj.uuid not in uids:
                setattr(obj, id_field_name, None)
            elif obj.uuid in uids:
                setattr(obj, id_field_name, myuid)

    def _set_link_nn_rev(
        self,
        basetypename: str,
        id_field_name: str,
        values: Sequence["MxlimsImplementation"]
    ):
        """Setter for n..n reverse link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, Sample, LogisticalSample)
        :param id_field_name:
        :param values:
        :return:
        """
        myuid = self.uuid
        uids = list(obj.uuid for obj in values)
        for obj in self._objects_by_id[basetypename].values():
            revuids = getattr(obj, id_field_name)
            if myuid in revuids and obj.uuid not in uids:
                revuids.remove(myuid)
            elif obj.uuid in uids:
                revuids.add(myuid)

class BaseMessage(BaseModel):
    """Class for basic MxlimsMessage holding message implementation"""

    @classmethod
    def from_pydantic_objects(
            cls, contents: Sequence[MxlimsImplementation]
    ) -> "BaseMessage":
        """Generate a filled-in Message from a list of MxlimsImplementation objects

        :param contents:
        :return:
        """
        result  = cls()
        for obj in contents:
            camel_type = obj.mxlims_type
            snake_type = camel_to_snake(camel_type)
            objdict = getattr(result, snake_type, None)
            if objdict is None:
                raise ValueError(
                    f"Message {cls.__name__} cannot contain {camel_type} "
                )
            else:
                ind = len(objdict) + 1
                objdict[f"{camel_type}{ind}"] = obj
        return result

    @classmethod
    def from_message_file(
            cls,
            message_path: Path,
            uuid_clash_mode: UuidClashMode = UuidClashMode.reject_new,
            merge_links: bool = True
    ) -> "BaseMessage":
        """Load schema-compliant JSON message into main implementation

        Args:
            message_path: Path to message JSON file
            merge_mode: In case of uuid clash should incoming objects replace or defer to existing
            merge_links: Should -to-many links be merged between incoming and existing objects
                         Relevant only for Job,inputData, job,referenceData, and Job,templateData

        Returns:

        """
        temp_message = cls()
        message_dict= json.loads(message_path.read_text())
        to_import_json(message_dict, uuid_clash_mode=uuid_clash_mode)
        for tag in message_dict:
            snaketag = camel_to_snake(tag)
            if not hasattr(temp_message, snaketag):
                raise ValueError(
                    f"class {cls.__name__} does not have attribute {snaketag}"
                )
        return cls.model_validate(message_dict)

    def export_message(self, message_file: Path):
        """ Export message to message_file

        :param message_path:
        :return:
        """
        # The stringification is needed because model_dump_json required for UUID
        message_str = self.model_dump_json(
            indent=4,
            by_alias=True,
            exclude_none=True,
            serialize_as_any=True,
        )
        message_json = json.loads(message_str)
        to_export_json(message_json)
        message_file.write_text(json.dumps(message_json, indent=4))

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
    uuid_to_id = {}
    for tag, dd1 in message_dict.items():
        if tag == "version":
            # Special case - the only non-dictionary property
            continue
        elif dd1:
            for tag2, dd2 in dd1.items():
                uuid_to_id[dd2["uuid"]]= (dd2["mxlimsType"], f"#/{tag}/{tag2}")

    for tag, objdict in list(message_dict.items()):
        if not objdict:
            message_dict.pop(tag)
        elif tag == "version":
            # Special case - the only non-dictionary property
            continue
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
                            tpl = uuid_to_id.get(link_uid)
                            if tpl:
                                # The linked-to object is in the message
                                obj[linkdict["link_ref_name"]] = {
                                    "$ref": tpl[1]
                                }
                            else:
                                base_type = linkdict["basetypename"]
                                if base_type in message_dict:
                                    # Object not in message.
                                    # Put Stub link, if allowed
                                    target_dict = message_dict[base_type]
                                    obj[linkdict["link_ref_name"]] = {
                                        "$ref": f"/{base_type}/{base_type}{len(target_dict)}"
                                    }
                                    # And add stub to the message
                                    target_dict[str(link_uid)] = {
                                        "mxlimsBaseType": base_type,
                                        "uuid": str(link_uid)
                                    }
                    else:
                        # Multiple link - link_uid is a list
                        if link_uid:
                            obj[linkdict["link_ref_name"]] = reflist = []
                            for luid in link_uid:
                                tpl = uuid_to_id.get(luid)
                                if tpl:
                                    # The linked-to object is in the message
                                    newref = {
                                        "$ref": tpl[1]
                                    }
                                else:
                                    base_type = linkdict["basetypename"]
                                    if base_type in message_dict:
                                        # Object not in message.
                                        # Put Stub link, if allowed
                                        target_dict = message_dict[base_type]
                                        newref = {
                                            "$ref": f"/{base_type}/{base_type}{len(target_dict)}",
                                        }
                                        # And add stub to the message
                                        target_dict[str(luid)] = {
                                            "mxlimsBaseType": base_type,
                                            "uuid": str(luid),
                                        }
                                reflist.append(newref)


def to_import_json(
        message_dict: dict,
        uuid_clash_mode: UuidClashMode = UuidClashMode.reject_new
) -> None:
    """Convert JSON read from schema-compliant JSON files to pydantic-compliant

    Conversion is done in-place

    :param message_dict: schema-compliant JSON message
    :return:
    """
    for tag, objdict in list(message_dict.items()):
        # Add uuid for objects lacking them
        if tag == "version":
            continue
        for obj in objdict.values():
            if not obj.get("uuid"):
                if tag in CORETYPES:
                    raise ValueError(f"{tag} stub lacks uuid")
                obj["uuid"] = str(uuid.uuid1())
    for tag, objdict in list(message_dict.items()):
        if tag == "version":
            continue
        refdict = LINK_SPECIFICATION.get(tag)
        for obj in objdict.values():
            # Convert link references to foreign-key uuid values
            for linkdict in refdict["links"].values():
                link_id_name_orig = linkdict.get("link_id_name")
                link_ref_name = linkdict.get("link_ref_name")
                if link_id_name_orig:
                    # This is a link with a foreign key
                    link_id_name = snake_to_camel(link_id_name_orig)
                    data = obj.pop(link_ref_name, None)
                    if data:
                        if linkdict["cardinality"] == "single":
                            tags = data["$ref"].split("/", 2)[-2:]
                            obj[link_id_name] = (
                                message_dict[tags[0]][tags[1]]["uuid"]
                            )
                        else:
                            uids = obj[link_id_name] = []
                            for ddref in data:
                                tags = ddref["$ref"].split("/", 2)[-2:]
                                uids.append(
                                    message_dict[tags[0]][tags[1]]["uuid"]
                                )
    for tag in CORETYPES:
        # Remove Stub objects - we no longer need them to disambiguate links
        message_dict.pop(tag, None)

    for tag, objdict in list(message_dict.items()):
        # handle uuid clashes between new and existing objects
        if tag == "version":
            continue
        for tag2, new_obj in objdict.items():
            old_obj = MxlimsImplementation.get_object_by_uuid(new_obj["uuid"])
            if old_obj is not None:
                if uuid_clash_mode == UuidClashMode.reject_new:
                    print(f"Uuid clash for {new_obj['uuid']}, ignore new object")
                    del objdict[tag2]
                elif uuid_clash_mode == UuidClashMode.update_old:
                    print(f"Uuid clash for {new_obj['uuid']}, update old object")
                    for tag3, val in new_obj.items():
                        setattr(old_obj, tag3, val)
                else:
                    # we must have an error
                    raise ValueError(f"Uuid clash for {new_obj['uuid']}")

