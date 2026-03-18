from quanter_swarm.specialists.feature_engineering_specialist import FeatureEngineeringSpecialist


def test_feature_engineering_specialist_wraps_features() -> None:
    payload = FeatureEngineeringSpecialist().build(
        {
            "market_packet": {"change_pct": 0.02, "volatility": 0.03, "avg_volume": 1_000_000},
            "fundamentals_packet": {"valuation": 1.0, "quality": 0.8},
            "shares_float_packet": {"float_shares": 10_000_000},
        }
    )
    assert "features" in payload
    assert "float_turnover" in payload["features"]
