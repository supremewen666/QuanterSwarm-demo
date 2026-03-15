"""Validate key configs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.cli import validate_repo_configs


def main() -> None:
    validation = validate_repo_configs()
    if not validation["ok"]:
        parts = []
        if validation["missing"]:
            parts.append(f"missing={','.join(validation['missing'])}")
        if validation["invalid"]:
            parts.append(f"invalid={','.join(validation['invalid'])}")
        if validation["unknown_leaders"]:
            parts.append(f"unknown_leaders={','.join(validation['unknown_leaders'])}")
        print("configs_invalid:" + ";".join(parts))
        raise SystemExit(1)
    print("configs_ok")


if __name__ == "__main__":
    main()
