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

import re

from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):

    class Config:
        populate_by_name = True
        extra = "forbid"
        use_enum_values = True
        validation_error_cause = True

def camel_to_snake(name: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()

def snake_to_camel(name:str) -> str:
    ll0 =  name.split("_")
    if len(ll0) < 2:
        return name
    return ll0[0] + "".join(txt.capitalize() for txt in ll0[1:])


