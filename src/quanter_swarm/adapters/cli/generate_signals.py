"""Generate structured signals from the internal simulation source."""

from __future__ import annotations

import argparse

from quanter_swarm.application import GenerateSignals
from quanter_swarm.application.task_flows import INTERNAL_SIM_SOURCE, write_output_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate QuanterSwarm signals.")
    parser.add_argument(
        "--source",
        default=INTERNAL_SIM_SOURCE,
        choices=(INTERNAL_SIM_SOURCE,),
        help="Signal source. Only internal_sim is supported.",
    )
    parser.add_argument("--date", default=None, help="Optional as-of date label for generated artifacts.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Optional symbol override.")
    parser.add_argument("--output", default=None, help="Optional JSON output file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = GenerateSignals().execute(source=args.source, symbols=args.symbols, as_of_date=args.date)
    print(write_output_payload(payload, args.output))


if __name__ == "__main__":
    main()
