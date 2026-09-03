import json
from pathlib import Path
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

def modify_files(schema_dir):
    schema_dir = Path(schema_dir)

    # Use rglob to recursively find all .json files
    for schema_file in schema_dir.rglob("*.json"):
        lines = open(schema_file).readlines()
        line = (
            '    "$id": "https://mxlims.org/schemas/%s/%s",\n'
            % (schema_file.parts[-2], schema_file.name)
        )
        lines.insert(1,line)
        open(schema_file, "w").write("".join(lines))
if __name__ == "__main__":
    target = Path(__file__).parent.parent / "schemas"
    modify_files(target)