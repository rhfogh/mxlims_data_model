import abc
from typing import Any, ClassVar
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
        uid = self.uuid
        if uid in obj_by_id:
            raise ValueError(
                f"{self.mxlims_base_type} with uuid '{uid}' already exists"
            )
        else:
            obj_by_id[uid] = self