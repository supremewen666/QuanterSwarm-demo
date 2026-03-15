from quanter_swarm.specialists.feature_engineering_specialist import FeatureEngineeringSpecialist


def test_feature_engineering_specialist_wraps_features() -> None:
    assert "features" in FeatureEngineeringSpecialist().build({"a": 1})
