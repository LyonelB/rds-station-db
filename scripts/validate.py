#!/usr/bin/env python3
"""validate.py - Validates all country JSON files against _schema.json"""
import json, sys, re
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Missing dependency: pip install jsonschema")
    sys.exit(1)

DATA_DIR   = Path(__file__).parent.parent / "data"
SCHEMA_FILE = DATA_DIR / "_schema.json"

def load_schema():
    with open(SCHEMA_FILE) as f: return json.load(f)

def validate_file(path, schema):
    errors = []
    with open(path) as f:
        try: data = json.load(f)
        except json.JSONDecodeError as e: return [f"JSON parse error: {e}"]
    validator = jsonschema.Draft7Validator(schema)
    for err in validator.iter_errors(data):
        errors.append(f"Schema: {err.message} (path: {list(err.path)})")
    if "stations" in data:
        pi_seen = {}
        for i, s in enumerate(data["stations"]):
            pi = s.get("pi","")
            if pi in pi_seen: errors.append(f"Station [{i}] duplicate PI '{pi}' (also at {pi_seen[pi]})")
            else: pi_seen[pi] = i
            ps = s.get("ps","")
            if len(ps) > 8: errors.append(f"Station [{i}] PI={pi}: PS '{ps}' exceeds 8 chars ({len(ps)})")
    return errors

def main():
    schema = load_schema()
    all_ok = True
    files = [f for f in sorted(DATA_DIR.glob("*.json")) if f.name != "_schema.json"]
    if not files: print("No country JSON files found"); sys.exit(1)
    for path in files:
        errors = validate_file(path, schema)
        if errors:
            all_ok = False
            print(f"\n❌  {path.name}")
            for e in errors: print(f"   • {e}")
        else:
            with open(path) as f: n = len(json.load(f).get("stations",[]))
            print(f"✅  {path.name} ({n} stations)")
    print()
    if all_ok: print("All files valid."); sys.exit(0)
    else: print("Validation failed."); sys.exit(1)

if __name__ == "__main__": main()
