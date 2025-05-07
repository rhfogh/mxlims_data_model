import abc
from typing import Any, ClassVar, List, Optional
from weakref import WeakValueDictionary
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):

    class Config:
        populate_by_name = True
        extra = "forbid"
        use_enum_values = True
        validation_error_cause = True

    # Class-level container for implementation of access-object-by-id
    _objects_by_id: ClassVar[dict] = {
        "Dataset": WeakValueDictionary(),
        "Job": WeakValueDictionary(),
        "PreparedSample": WeakValueDictionary(),
        "LogisticalSample": WeakValueDictionary(),
    }

class MxlimsImplementation:

    # Class-level container for implementation of access-object-by-id
    _objects_by_id: ClassVar[dict] = {
        "Dataset": WeakValueDictionary(),
        "Job": WeakValueDictionary(),
        "PreparedSample": WeakValueDictionary(),
        "LogisticalSample": WeakValueDictionary(),
    }

    @property
    @abc.abstractmethod
    def uuid(self):
        pass

    @property
    @abc.abstractmethod
    def mxlims_base_type(self):
        pass

    @property
    @abc.abstractmethod
    def mxlims_type(self):
        pass

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
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
        values: List["MxlimsImplementation"]
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
            for obj in self._objects_by_id[basetypename]
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
            for obj in self._objects_by_id[basetypename]
            if myuid in getattr(obj, id_field_name)
        )
        return result

    def _set_link_1n_rev(
        self,
        basetypename: str,
        id_field_name: str,
        values: List["MxlimsImplementation"]
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
        for obj in self._objects_by_id[basetypename]:
            if getattr(obj, id_field_name) == myuid and obj.uuid not in uids:
                setattr(obj, id_field_name, None)
            elif obj.uuid in uids:
                setattr(obj, id_field_name, myuid)

    def _set_link_nn_rev(
        self,
        basetypename: str,
        id_field_name: str,
        values: List["MxlimsImplementation"]
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
        for obj in self._objects_by_id[basetypename]:
            revuids = getattr(obj, id_field_name)
            if myuid in revuids and obj.uuid not in uids:
                revuids.remove(myuid)
            elif obj.uuid in uids:
                revuids.add(myuid)

class BaseMessage:
    """Class for basic MxlimsMessage holding message implementation"""