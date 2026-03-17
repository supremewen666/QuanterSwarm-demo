"""Application entry point."""

from __future__ import annotations

import json

from quanter_swarm.orchestrator.root_agent import RootAgent
from quanter_swarm.utils.logging import configure_logging


def main() -> None:
    configure_logging()
    print(json.dumps(RootAgent().run_sync(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
