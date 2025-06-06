# generated by datamodel-codegen:
#   filename:  datatypes/ReflectionFileType.json

from __future__ import annotations

from enum import Enum


class ReflectionFileType(Enum):
    """
    Name for file type, used in ReflectionSet class
    """

    SCALED_AND_MERGED_MTZ = "scaled and merged MTZ"
    SCALED_AND_UNMERGED_MTZ = "scaled and unmerged MTZ"
    UNMERGED_MTZ = "unmerged MTZ"
    XDS_INTEGRATE_HKL__UNMERGED__HTTPS___XDS_MR_MPG_DE_HTML_DOC_XDS_FILES_HTML_INTEGRATE_HKL_ = "XDS INTEGRATE.HKL; unmerged (https://xds.mr.mpg.de/html_doc/xds_files.html#INTEGRATE.HKL)"
    XDS_XDS_ASCII_HKL__SCALED_AND_UNMERGED__HTTPS___XDS_MR_MPG_DE_HTML_DOC_XDS_FILES_HTML_XDS_ASCII_HKL_ = "XDS XDS_ASCII.HKL; scaled and unmerged (https://xds.mr.mpg.de/html_doc/xds_files.html#XDS_ASCII.HKL)"
