from typing import ClassVar
from weakref import WeakValueDictionary
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):

    class Config:
        populate_by_name = True
        extra = "forbid"
        use_enum_values = True
        validation_error_cause = True

    # Containers for implementation access-object-by-id
    datasets_by_id: ClassVar[WeakValueDictionary] = WeakValueDictionary()
    jobs_by_id: ClassVar[WeakValueDictionary] = WeakValueDictionary()
    prepared_samples_by_id: ClassVar[WeakValueDictionary] = WeakValueDictionary()
    logistical_samples_by_id: ClassVar[WeakValueDictionary] = WeakValueDictionary()
