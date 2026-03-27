"""Application entry point."""

from __future__ import annotations

import json

from quanter_swarm.application import RunResearchCycle
from quanter_swarm.core.runtime.logging import configure_logging


def main() -> None:
    configure_logging()
    print(json.dumps(RunResearchCycle().execute(symbol="AAPL"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
