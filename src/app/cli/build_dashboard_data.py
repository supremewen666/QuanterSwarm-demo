"""Build dashboard-ready dataset artifacts."""

from __future__ import annotations

import argparse

from app.services.common import INTERNAL_SIM_SOURCE, write_output_payload
from quanter_swarm.application import BuildDashboardData


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build QuanterSwarm dashboard dataset.")
    parser.add_argument(
        "--source",
        default=INTERNAL_SIM_SOURCE,
        choices=(INTERNAL_SIM_SOURCE,),
        help="Dashboard source. Only internal_sim is supported.",
    )
    parser.add_argument("--with-alpaca-readonly", action="store_true", help="Enable readonly Alpaca enrichment.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Optional symbol override.")
    parser.add_argument("--output", default=None, help="Optional JSON output file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = BuildDashboardData().execute(
        source=args.source,
        symbols=args.symbols,
        with_alpaca_readonly=args.with_alpaca_readonly,
    )
    print(write_output_payload(payload, args.output))


if __name__ == "__main__":
    main()
