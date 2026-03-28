import json
from pathlib import Path
from typing import Any

from quanter_swarm.agents.orchestrator import RootAgent

GOLDEN_DIR = Path("tests/golden")


def _subset(payload: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in template.items():
        if isinstance(value, dict):
            nested_payload = payload.get(key)
            output[key] = _subset(nested_payload if isinstance(nested_payload, dict) else {}, value)
        else:
            output[key] = payload.get(key)
    return output


def test_research_cycle_matches_golden_for_aapl() -> None:
    report = RootAgent().run_sync(symbol="AAPL")
    golden = json.loads((GOLDEN_DIR / "research_cycle_aapl.json").read_text(encoding="utf-8"))
    assert _subset(report, golden) == golden


def test_research_cycle_no_trade_matches_golden_for_msft() -> None:
    report = RootAgent().run_sync(symbol="MSFT")
    golden = json.loads((GOLDEN_DIR / "research_cycle_msft_no_trade.json").read_text(encoding="utf-8"))
    assert _subset(report, golden) == golden
    assert report["portfolio_suggestion"]["positions"] == []


def test_research_cycle_matches_golden_for_nvda() -> None:
    report = RootAgent().run_sync(symbol="NVDA")
    golden = json.loads((GOLDEN_DIR / "research_cycle_nvda.json").read_text(encoding="utf-8"))
    assert _subset(report, golden) == golden


def test_markdown_output_contains_required_outline_sections() -> None:
    report = RootAgent().run_sync(symbol="AAPL")
    markdown = report["markdown_summary"]
    outline = (GOLDEN_DIR / "research_cycle_outline.md").read_text(encoding="utf-8")
    for heading in [line for line in outline.splitlines() if line.startswith("## ")]:
        assert heading in markdown
