import json
import jsonschema
from pathlib import Path
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

BASE = Path(__file__).parent
def retrieve_from_filesystem(uri: str):
    if not uri.startswith("../"):
        raise NoSuchResource(ref=uri)
    path = BASE / Path(uri.removeprefix("../"))
    contents = json.loads(path.read_text())
    return Resource.from_contents(contents)

registry = Registry(retrieve=retrieve_from_filesystem)


if __name__ == "__main__":
    instance = BASE / "dttest" / "tst_instance.json"
    schema = BASE / "schem" / "DropImageData.json"
    jsonschema.validate(
        instance=json.load(open(instance)),
        schema=json.load(open(schema)),
        registry=registry
    )
