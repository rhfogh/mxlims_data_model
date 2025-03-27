
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):

    class Config:
        populate_by_name = True
        extra = "forbid"
        extra = "forbid"
        use_enum_values = True
