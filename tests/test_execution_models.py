from quanter_swarm.execution.fills import decide_fill_status, estimate_fill_ratio
from quanter_swarm.execution.slippage import estimate_slippage_bps


def test_slippage_model_increases_with_volatility_and_participation() -> None:
    low = estimate_slippage_bps(base_bps=5, volatility=0.01, participation_rate=0.01, is_open=False)
    high = estimate_slippage_bps(base_bps=5, volatility=0.05, participation_rate=0.2, is_open=True)
    assert high > low


def test_fill_ratio_model_supports_partial_fills() -> None:
    ratio = estimate_fill_ratio(participation_rate=0.3, volatility=0.08, fill_model="partial")
    assert 0.35 <= ratio <= 1.0


def test_fill_status_supports_delayed_and_unfilled() -> None:
    delayed = decide_fill_status(participation_rate=0.2, volatility=0.09, event_window=True, fill_ratio=0.6)
    unfilled = decide_fill_status(participation_rate=0.5, volatility=0.03, event_window=False, fill_ratio=0.4)
    assert delayed == "delayed"
    assert unfilled == "unfilled"
