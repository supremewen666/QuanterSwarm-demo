"""Serve the lightweight dashboard app."""

from __future__ import annotations

import argparse

import uvicorn

from quanter_swarm.application.task_flows import DEFAULT_HOST, DEFAULT_PORT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the QuanterSwarm dashboard.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Bind host.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    uvicorn.run("quanter_swarm.adapters.dashboard.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
