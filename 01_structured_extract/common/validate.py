import json
import pathlib
from jsonschema import validate, ValidationError

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

def load_text(path: str | pathlib.Path = "samples/paper.txt") -> str:
    p = (BASE_DIR / path) if not str(path).startswith(str(BASE_DIR)) else pathlib.Path(path)
    return p.read_text(encoding="utf-8")

def strip_code_fences(s: str) -> str:
    """Remove markdown code fences (```json ... ```) from response string.
    
    Some models wrap JSON output in code fences, this function removes them.
    """
    s = s.strip()
    if s.startswith("```"):
        # Remove opening fence and language tag
        first = s.find("\n")
        if first != -1:
            s = s[first+1:]
        # Remove closing fence
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()

def parse_json(maybe_json: str | dict) -> dict:
    if isinstance(maybe_json, dict):
        return maybe_json
    txt = strip_code_fences(maybe_json)
    try:
        return json.loads(txt)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[JSONError] {e}\nRaw content:\n{maybe_json[:500]}")

def validate_and_print(obj: dict, schema: dict) -> None:
    try:
        validate(instance=obj, schema=schema)
    except ValidationError as e:
        path = "/".join(map(str, e.path)) if e.path else "(root)"
        raise SystemExit(f"[SchemaError] {e.message}\nPath: {path}")
    import pprint
    print("✓ JSON matches schema")
    pprint.pp(obj, sort_dicts=False)

def save_json(obj: dict, out_path: str | pathlib.Path) -> None:
    out_path = (BASE_DIR / out_path) if not str(out_path).startswith(str(BASE_DIR)) else pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ Saved: {out_path.relative_to(BASE_DIR)}")