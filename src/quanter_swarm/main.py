"""Application entry point."""

from __future__ import annotations

import json

from quanter_swarm.orchestrator.root_agent import RootAgent


def main() -> None:
    print(json.dumps(RootAgent().run_sync(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
