"""Validate the repository configs used by the skill."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.cli import validate_repo_configs


def main() -> None:
    validation = validate_repo_configs(ROOT / "configs")
    if not validation["ok"]:
        parts = []
        if validation["missing"]:
            parts.append(f"missing={','.join(validation['missing'])}")
        if validation["invalid"]:
            parts.append(f"invalid={','.join(validation['invalid'])}")
        if validation["unknown_leaders"]:
            parts.append(f"unknown_leaders={','.join(validation['unknown_leaders'])}")
        print("config_validation_failed:" + ";".join(parts))
        raise SystemExit(1)
    print("config_validation_ok")


if __name__ == "__main__":
    main()
