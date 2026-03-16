"""Run walk-forward backtest."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quanter_swarm.backtest.walk_forward import WalkForwardBacktester


def main() -> None:
    parser = argparse.ArgumentParser(description="Run walk-forward backtest.")
    parser.add_argument("--symbols", default="AAPL,MSFT,NVDA", help="Comma-separated symbols.")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--capital", type=float, default=100_000.0)
    args = parser.parse_args()

    symbols = [item.strip() for item in args.symbols.split(",") if item.strip()]
    payload = WalkForwardBacktester().run(symbols=symbols, steps=args.steps, capital=args.capital)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
