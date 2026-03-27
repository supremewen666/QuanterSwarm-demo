from quanter_swarm.services.execution.slippage import apply_slippage, estimate_slippage_bps


def test_estimate_slippage_bps_not_fixed_constant() -> None:
    base = estimate_slippage_bps(base_bps=5, volatility=0.01, participation_rate=0.01, is_open=False)
    stressed = estimate_slippage_bps(base_bps=5, volatility=0.08, participation_rate=0.3, is_open=True)
    assert stressed > base


def test_apply_slippage_changes_price() -> None:
    assert apply_slippage(100, 10) > 100
