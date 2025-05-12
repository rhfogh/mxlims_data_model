#! /usr/bin/env python
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

__copyright__ = """ Copyright © 2024 -  2025 MXLIMS collaboration."""
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

import enum
import json
from pathlib import Path
from typing import ClassVar, List, Optional, Sequence
# from weakref import WeakValueDictionary
from mxlims.impl.utils import camel_to_snake, to_import_json
from pydantic import BaseModel as PydanticBaseModel
from ruamel.yaml import YAML

yaml = YAML(typ="safe", pure=True)
# The following are not needed for load, but define the default style.
yaml.default_flow_style = False
yaml.indent(mapping=4, sequence=4, offset=2)

with (Path(__file__).parent / "link_specification.yaml").open(encoding="utf-8") as fp0:
    LINK_SPECIFICATION = yaml.load(fp0)

class MergeMode(enum.Enum):
    """Enumeration for input merging mode to use when uuids clash

    Determines whetehr the input objetc will replace or be replaced by the existing,
    or hetehr there will be an error.

    Merging of -to-many links (of Jobs) is cont5rolled by the merge_links parameter"""

    replace = "replace"
    defer = "defer"
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
        "PreparedSample": dict(),
        "LogisticalSample": dict(),
    }

    def __init__(self, ) -> None:
        obj_by_id = self._objects_by_id[self.mxlims_base_type]
        myuid = self.uuid
        if myuid in obj_by_id:
            raise ValueError(
                f"{self.mxlims_base_type} with uuid '{myuid}' already exists"
            )
        else:
            obj_by_id[myuid] = self

    def _get_link_n1(
            self,
            basetypename: str,
            id_field_name: str
    ) -> Optional["MxlimsImplementation"]:
        """Getter for n..1 forward link

        :param basetypename: Name of target base abstract class
            (Job, Dataset, PreparedSample, LlogisticalSample)
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
            (Job, Dataset, PreparedSample, LogisticalSample)
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
            (Job, Dataset, PreparedSample, LogisticalSample)
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
            (Job, Dataset, PreparedSample, LogisticalSample)
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
            (Job, Dataset, PreparedSample, LogisticalSample)
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
            (Job, Dataset, PreparedSample, LogisticalSample)
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

class BaseMessage:
    """Class for basic MxlimsMessage holding message implementation"""

    @classmethod
    def from_pydantic_objects(cls, contents: Sequence[MxlimsImplementation]):
        result  = cls()
        for tag in ("mx_experiment", "mxExperiment", "MxExperiment"):
            print ('=--->', tag, getattr(result, tag, "not found"))
        for obj in contents:
            mxtype = camel_to_snake(obj.mxlims_type)
            objdict = getattr(result, mxtype, None)
            if objdict is None:
                raise ValueError(
                    f"Message {cls.__name__} cannot contain {mxtype} "
                )
            else:
                objdict[obj.uuid] = obj
        return result

    @classmethod
    def from_message_file(
            cls, message_path: Path, merge_mode: MergeMode, merge_links: bool
    ) -> None:
        """

        Args:
            message_path: Path to message JSON file
            merge_mode: In case of uuid clash should incoming obvjects replace or defer to existing
            merge_links: Should -to-many links be merged between incoming and existing objects
                         Relevant only for Job,inputData, job,referenceData, and Job,templateData

        Returns:

        """
        """Load schema-compliant JSON message into main implementation

        Args:
            message_dict:

        Returns:
        """
        message_dict= json.loads(message_path.read_text())
        to_import_json(message_dict)
        for tag in message_dict:
            if not hasattr(cls, tag):
                raise ValueError(
                    "class {cls.__name__} does not have attribute {tag}"
                )
        for tag, objdict in message_dict:
            for tag2, newobj in list(objdict.items()):
                uid = newobj.uuid
                basetype = newobj.mxlims_base_type
                oldobj = cls._objects_by_id[basetype].get(uid)
                if oldobj is not None:
                    # Handle uuid clashes
                    if merge_mode == MergeMode.error:
                        raise ValueError(f"{tag} with uuid {uid} already exists")
                    elif merge_mode == MergeMode.replace:
                        del cls._objects_by_id[basetype][uid]
                        toobj = newobj
                        fromobj = oldobj
                    else:
                        del objdict[uid]
                        toobj = oldobj
                        fromobj = newobj
                    if merge_links:
                        for linkdict in (
                            LINK_SPECIFICATION[toobj.mxlims_type]["links"].values()
                        ):
                            link_id_name = linkdict.get("link_id_name")
                            if link_id_name and linkdict["cardinality"] == "multiple":
                                # merge input and exiting links
                                uids = getattr(toobj, link_id_name)
                                for uid in getattr(fromobj, link_id_name):
                                    if uid not in uids:
                                        toobj._append_link_nn(link_id_name, uid)
        cls.model_validate(message_dict)

