"""Export a structured report to the data directory."""
# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.cli import build_cycle_parser, emit_report


def main() -> None:
    default_output = str(ROOT / "data" / "reports" / "skill_export_report.md")
    args = build_cycle_parser(
        "Export a QuanterSwarm report artifact.",
        default_output=default_output,
        default_format="markdown",
    ).parse_args()
    print(emit_report(symbol=args.symbol, output_format=args.format, output_path=args.output))


if __name__ == "__main__":
    main()
