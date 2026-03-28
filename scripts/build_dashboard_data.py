"""Script wrapper for dashboard dataset generation."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from quanter_swarm.adapters.cli.build_dashboard_data import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
