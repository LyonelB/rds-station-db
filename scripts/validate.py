#!/usr/bin/env python3
"""
validate.py - Validates all country JSON files against _schema.json
Run: python3 scripts/validate.py
Used by GitHub Actions CI on every PR.
"""

import json
import sys
import re
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Missing dependency: pip install jsonschema")
    sys.exit(1)

DATA_DIR = Path(__file__).parent.parent / "data"
SCHEMA_FILE = DATA_DIR / "_schema.json"

PI_RE = re.compile(r"^[0-9A-Fa-f]{4}$")


def load_schema():
    with open(SCHEMA_FILE) as f:
        return json.load(f)


def validate_file(path: Path, schema: dict) -> list[str]:
    errors = []
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return [f"JSON parse error: {e}"]

    # JSON Schema validation
    validator = jsonschema.Draft7Validator(schema)
    for err in validator.iter_errors(data):
        errors.append(f"Schema: {err.message} (path: {list(err.path)})")

    # Extra business rules
    if "stations" in data:
        seen_keys = {}
        for i, station in enumerate(data["stations"]):
            pi = station.get("pi", "")
            ps = station.get("ps", "")
            name = station.get("name", "")

            # Unicité : PI + PS + name (plusieurs services peuvent partager un PI)
            key = (pi, ps.strip(), name)
            if key in seen_keys:
                errors.append(
                    f"Station [{i}] duplicate PI+PS+name '{pi}/{ps}/{name}' "
                    f"(also at index {seen_keys[key]})"
                )
            else:
                seen_keys[key] = i

            # PS length
            if len(ps) > 8:
                errors.append(
                    f"Station [{i}] PI={pi}: PS '{ps}' exceeds 8 chars ({len(ps)})"
                )

    return errors


def main():
    schema = load_schema()
    all_ok = True

    files = sorted(DATA_DIR.glob("*.json"))
    files = [f for f in files if f.name != "_schema.json"]

    if not files:
        print("No country JSON files found in data/")
        sys.exit(1)

    for path in files:
        errors = validate_file(path, schema)
        if errors:
            all_ok = False
            print(f"\n❌  {path.name}")
            for err in errors:
                print(f"   • {err}")
        else:
            station_count = 0
            with open(path) as f:
                data = json.load(f)
                station_count = len(data.get("stations", []))
            print(f"✅  {path.name} ({station_count} stations)")

    print()
    if all_ok:
        print("All files valid.")
        sys.exit(0)
    else:
        print("Validation failed — see errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
