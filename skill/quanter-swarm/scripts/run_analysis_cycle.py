"""Run the project analysis cycle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.cli import build_cycle_parser, emit_report


def main() -> None:
    args = build_cycle_parser("Run one QuanterSwarm analysis cycle.").parse_args()
    print(emit_report(symbol=args.symbol, output_format=args.format, output_path=args.output))


if __name__ == "__main__":
    main()
