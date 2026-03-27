"""Run replayable backtests from the internal simulation source."""

from __future__ import annotations

import argparse

from app.services.common import DEFAULT_CAPITAL, INTERNAL_SIM_SOURCE, write_output_payload
from quanter_swarm.application import RunBacktest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run QuanterSwarm backtests.")
    parser.add_argument(
        "--source",
        default=INTERNAL_SIM_SOURCE,
        choices=(INTERNAL_SIM_SOURCE,),
        help="Research and backtest source. Only internal_sim is supported.",
    )
    parser.add_argument("--config", default=None, help="Optional backtest config path for artifact metadata.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Optional symbol override.")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL, help="Initial capital.")
    parser.add_argument("--output", default=None, help="Optional JSON output file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = RunBacktest().execute(
        source=args.source,
        symbols=args.symbols,
        config_path=args.config,
        capital=args.capital,
    )
    print(write_output_payload(payload, args.output))


if __name__ == "__main__":
    main()
