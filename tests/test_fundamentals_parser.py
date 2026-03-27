from quanter_swarm.services.research.fundamentals_parser import parse_fundamentals


def test_parse_fundamentals_uses_xbrl_and_filings_when_present() -> None:
    parsed = parse_fundamentals(
        {
            "valuation": 1.2,
            "growth": 0.4,
            "quality": 0.6,
            "leverage": 0.2,
            "xbrl_facts": [
                {"metric_name": "Revenues", "metric_value": 1000},
                {"metric_name": "NetIncomeLoss", "metric_value": 120},
            ],
            "sec_filings": [{"form": "10-K"}],
        }
    )
    assert parsed["xbrl_fact_count"] == 2
    assert parsed["filing_count"] == 1
    assert parsed["quality_score"] > 0
