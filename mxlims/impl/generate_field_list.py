
import json
from typing import Optional, List
from pathlib import Path

def generate_fields(dirname: Optional[str] = None) -> None :
    """
    Generate tab-separated table of model fields

    :param dirname: path to mxlims working directory
    :return:
    """
    if dirname:
        mxlims_dir = Path(dirname)
    else:
        mxlims_dir = Path.cwd()

    schema_dir = mxlims_dir / "mxlims" / "schemas"

    # Read all relevant schemas
    schemadata = {}
    for tag in ("data", "datatypes", "objects"):
        dd1 = schemadata[tag] = {}
        for fpath in (schema_dir / tag).iterdir():
            name = fpath.stem
            with fpath.open(encoding="utf-8") as fp0:
                dd1[name] = json.load(fp0)

    # Create Datatype dictionaries
    datatypes = {}
    for tag, dd1 in schemadata["datatypes"].items():
        props = dd1.get("properties")
        if props:
            datatypes[tag] = dd2 = {}
            for name, dd3 in props.items():
                typ, desc = get_type_desc(dd3)
                dd2[name]  = {"type": typ, "description": desc}

    # Create Data dictionaries
    data = {}
    for tag, dd1 in schemadata["data"].items():
        props = dd1.get("properties")
        if props:
            data[tag] = dd2 = {}
            for name, dd3 in props.items():
                typ, desc = get_type_desc(dd3)
                dd2[name]  = {"type": typ, "description": desc}

    # Write out per-field lines
    for tag, dd1 in sorted(schemadata["objects"].items()):
        ll1 = dd1.get("allOf", ())
        # annotation is special-cased as the only non-implementation field in MxlimsObject
        output = {"annnotation": "string\tComment or annotation."}
        if len(ll1) > 1:
            for dd2 in reversed(ll1):
                # Superclass first
                txt = dd2["$ref"]
                txt = txt.split("/")[-1]
                typ = txt.split(".")[0]
                dd3 = data.get(typ, {})
                for tag2, dd4 in dd3.items():
                    fulltag = ".".join((tag, tag2))
                    typ2 = dd4.get("type", "NOTYPE")
                    desc = dd4.get("description", "-")
                    datatype = datatypes.get(typ2)
                    if datatype:
                        for tag3, prop in datatype.items():
                            typ3 = prop.get("type", "NOTYPE")
                            desc = prop.get("description", "-")
                            output[".".join((fulltag, tag3))] = "\t".join((typ3, desc))
                    else:
                        output[fulltag] = "\t".join((typ2, desc))
            for name, val in output.items():
                print( "\t".join((name, val)))


def get_type_desc(adict: dict):
    desc = adict.get("description", "NONE")
    if "allOf" in adict:
        txt = adict["allOf"][0]["$ref"]
        txt = txt.split("/")[-1]
        typ = txt.split(".")[0]
    elif "oneOf" in adict:
        # NB this is a hack. For e.g. DropRegion.region you have two alternative
        # $ref. We arbitrarily use the first one, as this comes closer
        txt = adict["oneOf"][0]["$ref"]
        txt = txt.split("/")[-1]
        typ = txt.split(".")[0]
    else:
        typ = adict.get("type", "XX1")
        if typ == "array":
            items = adict.get("items")
            if items:
                typ2 = adict["items"].get("type")
                if not typ2:
                    typ2 = adict["items"]["$ref"].split("/")[-1].split(".")[0]
            else:
                items = adict["prefixItems"]
                typ2 = items[0]["type"]
            typ = f"array[{typ2}]"
    return  typ, desc


if __name__ == "__main__":

    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(
        prog="generate_field_list.py",
        formatter_class=RawTextHelpFormatter,
        prefix_chars="--",
        description="""
MXLIMS code generation helper. Assumes standard directory structure""",
    )

    parser.add_argument(
        "--dirname",
        metavar="dirname",
        default=None,
        help="Path to directory containing mxlims/ and docs/ subdirectory\n",
    )

    argsobj = parser.parse_args()
    options_dict = vars(argsobj)

    field_data = generate_fields(**options_dict)