"""Run the skill adapter with a schema-first request payload."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.skill_interface import run_skill_request


def main() -> None:
    parser = argparse.ArgumentParser(description="Run skill contract request.")
    parser.add_argument("--request-json", required=True, help="Inline JSON string following research request contract.")
    parser.add_argument("--mode", choices=("normal", "degraded", "missing_data", "no_trade"), default="normal")
    parser.add_argument("--output", default=None, help="Optional output path for JSON response.")
    args = parser.parse_args()

    payload = run_skill_request(json.loads(args.request_json), mode=args.mode)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        print(str(destination))
        return
    print(rendered)


if __name__ == "__main__":
    main()
