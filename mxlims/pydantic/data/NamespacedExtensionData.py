# generated by datamodel-codegen:
#   filename:  data/NamespacedExtensionData.json

from __future__ import annotations

from mxlims.impl.MxlimsBase import BaseModel

from pydantic import Field


class NamespacedExtensionData(BaseModel):
    """
    JSON schema for extending MxlimsData. To be subclassed
    """

    namespace: str = Field(
        ...,
        description="Namespace string defining 'owner' of the namespace, e.g. 'ESRF, 'GPhL",
        title="Namespace",
    )
