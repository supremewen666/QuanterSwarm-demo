"""Run QuanterSwarm ablation experiments."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.services.backtest.experiment_runner import ExperimentRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QuanterSwarm ablation experiment.")
    parser.add_argument("experiment_type", choices=("router_ablation", "specialist_ablation", "allocation_ablation"))
    parser.add_argument("symbol", nargs="?", default="AAPL")
    args = parser.parse_args()
    payload = ExperimentRunner().run(args.experiment_type, args.symbol)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
