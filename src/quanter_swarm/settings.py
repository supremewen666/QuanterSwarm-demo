"""Application settings."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    environment: str = "dev"
    execution_mode: str = "paper"
    data_dir: Path = Path("data")
    config_dir: Path = Path("configs")
    default_symbols: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "NVDA"])
    starting_capital: float = 100_000.0
