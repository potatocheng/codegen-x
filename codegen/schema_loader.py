import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).parent / "schemas"

@lru_cache(maxsize=8)
def load_schema(name: str) -> Dict:
    path = SCHEMA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return json.loads(path.read_text(encoding='utf-8'))

def validate_json_against_schema(data: Dict, schema: Dict) -> List[str]:
    validator = Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(data):
        path = ".".join([str(p) for p in err.path]) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors
