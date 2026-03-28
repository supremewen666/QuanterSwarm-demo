"""Replay a stored research run."""

from __future__ import annotations

import argparse

from quanter_swarm.application import RunReplay
from quanter_swarm.application.task_flows import DEFAULT_CAPITAL, write_output_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay a QuanterSwarm run artifact.")
    parser.add_argument("--run-id", required=True, help="Artifact suffix or full run identifier.")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL, help="Replay capital base.")
    parser.add_argument("--output", default=None, help="Optional JSON output file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = RunReplay().execute(run_id=args.run_id, capital=args.capital)
    print(write_output_payload(payload, args.output))


if __name__ == "__main__":
    main()
