"""Shared router functions."""

from __future__ import annotations

from typing import Any

from quanter_swarm.config.defaults import DEFAULT_MAX_SPECIALISTS_PER_CYCLE, DEFAULT_TOKEN_BUDGET

_COST_ORDER = {"low": 0, "medium": 1, "high": 2}
_TOKEN_BUDGET_LIMITS = {"low": 1, "medium": 2, "high": 4}
_LATENCY_BUDGET_LIMITS = {
    "tight": 1,
    "low": 1,
    "medium": 2,
    "balanced": 2,
    "high": 4,
    "relaxed": 4,
}


def _resolved_config(router_config: dict[str, Any]) -> dict[str, Any]:
    nested = router_config.get("router")
    if isinstance(nested, dict):
        return {**router_config, **nested}
    return router_config


def _filter_capable_leaders(
    leaders: list[str],
    regime_label: str,
    skipped_reasons: dict[str, str],
) -> list[str]:
    from quanter_swarm.agents.registry import get_leader

    capable: list[str] = []
    for leader_name in leaders:
        leader = get_leader(leader_name)
        if leader.supports_regime(regime_label):
            capable.append(leader_name)
        else:
            skipped_reasons[leader_name] = "unsupported_regime_capability"
    return capable


def _specialist_sort_key(name: str, *, prefer_low_cost: bool) -> tuple[int, int, str]:
    from quanter_swarm.agents.registry import get_specialist

    specialist = get_specialist(name)
    priority = int(getattr(specialist, "priority", 0))
    cost = int(_COST_ORDER.get(str(getattr(specialist, "cost_hint", "medium")), 1))
    if prefer_low_cost:
        return (cost, -priority, name)
    return (-priority, cost, name)


def _latency_specialist_limit(latency_budget: Any) -> int | None:
    if latency_budget is None:
        return None
    if isinstance(latency_budget, (int, float)):
        if latency_budget <= 1.5:
            return 1
        if latency_budget <= 3.0:
            return 2
        return 4
    return _LATENCY_BUDGET_LIMITS.get(str(latency_budget).lower())


def select_specialist_plan(
    regime: str,
    task: str | None = None,
    router_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from quanter_swarm.agents.registry import registry

    resolved = _resolved_config(router_config or {})
    token_budget = str(resolved.get("token_budget", DEFAULT_TOKEN_BUDGET)).lower()
    latency_budget = resolved.get("latency_budget")
    max_specialists = int(
        resolved.get("max_specialists_per_cycle", DEFAULT_MAX_SPECIALISTS_PER_CYCLE)
    )
    token_limit = _TOKEN_BUDGET_LIMITS.get(token_budget, _TOKEN_BUDGET_LIMITS["medium"])
    latency_limit = _latency_specialist_limit(latency_budget)
    prefer_low_cost = token_limit <= 1 or (latency_limit is not None and latency_limit <= 1)

    selected: list[str] = []
    rejected: dict[str, str] = {}
    budget_constraints: dict[str, Any] = {
        "token_budget": token_budget,
        "latency_budget": latency_budget,
        "max_specialists_per_cycle": max_specialists,
        "token_budget_limit": token_limit,
    }
    if latency_limit is not None:
        budget_constraints["latency_budget_limit"] = latency_limit

    candidates: list[str] = []
    for name in registry.registered_names():
        agent = registry.create(name)
        if agent.role != "specialist":
            continue
        supported_regimes = getattr(agent, "supported_regimes", ())
        supported_tasks = getattr(agent, "supported_tasks", ())
        supports_regime = not supported_regimes or regime in supported_regimes
        supports_task = task is None or not supported_tasks or task in supported_tasks
        if supports_regime and supports_task:
            candidates.append(name)

    ranked = sorted(candidates, key=lambda name: _specialist_sort_key(name, prefer_low_cost=prefer_low_cost))
    budgeted = list(ranked)

    if len(budgeted) > token_limit:
        dropped = budgeted[token_limit:]
        budgeted = budgeted[:token_limit]
        for name in dropped:
            rejected[name] = "dropped_by_token_budget"

    if latency_limit is not None and len(budgeted) > latency_limit:
        dropped = budgeted[latency_limit:]
        budgeted = budgeted[:latency_limit]
        for name in dropped:
            rejected[name] = "dropped_by_latency_budget"

    if max_specialists > 0 and len(budgeted) > max_specialists:
        dropped = budgeted[max_specialists:]
        budgeted = budgeted[:max_specialists]
        for name in dropped:
            rejected[name] = "dropped_by_max_specialists_per_cycle"

    selected.extend(budgeted)
    return {
        "selected": selected,
        "rejected": rejected,
        "budget_constraints": budget_constraints,
    }


def select_leader(
    regime: str | dict[str, Any],
    router_config: dict[str, Any],
    regimes_config: dict[str, Any],
) -> dict[str, Any]:
    resolved = _resolved_config(router_config)
    regime_label = regime["label"] if isinstance(regime, dict) else regime
    regime_confidence = float(regime.get("confidence", 1.0)) if isinstance(regime, dict) else 1.0
    configured = regimes_config.get("regimes", {}).get(regime_label, {})
    selected_reasons: dict[str, str] = {}
    skipped_reasons: dict[str, str] = {}
    leaders = _filter_capable_leaders(list(configured.get("leaders", [])), regime_label, skipped_reasons)
    weights = configured.get("weights", {})
    threshold = float(resolved.get("confidence_threshold", 0.45))
    low_conf_policy = resolved.get("low_confidence_policy", "fallback")
    fallback_regime = resolved.get("default_regime", "sideways")

    if not leaders:
        leaders = _filter_capable_leaders(
            list(regimes_config.get("regimes", {}).get(fallback_regime, {}).get("leaders", [])),
            fallback_regime,
            skipped_reasons,
        )
        for leader in leaders:
            selected_reasons[leader] = f"fallback_from_{regime_label}_to_{fallback_regime}"

    low_confidence = regime_confidence < threshold
    if low_confidence:
        fallback_leaders = list(configured.get("fallback_leaders", leaders[:1]))
        if low_conf_policy == "no_trade":
            for leader in leaders:
                skipped_reasons[leader] = "low_regime_confidence_no_trade_policy"
            leaders = []
        else:
            filtered = [leader for leader in leaders if leader in fallback_leaders]
            for leader in leaders:
                if leader in filtered:
                    selected_reasons[leader] = "low_regime_confidence_fallback_leader"
                else:
                    skipped_reasons[leader] = "removed_by_low_confidence_policy"
            leaders = filtered

    max_active_leaders = resolved.get("max_active_leaders")
    if isinstance(max_active_leaders, int) and max_active_leaders > 0:
        dropped = leaders[max_active_leaders:]
        for leader in dropped:
            skipped_reasons[leader] = "dropped_by_max_active_leaders"
        leaders = leaders[:max_active_leaders]
    for leader in leaders:
        selected_reasons.setdefault(leader, "selected_by_regime_routing")

    leader_weights = {
        leader: round(float(weights.get(leader, 1 / max(1, len(leaders)))), 4)
        for leader in leaders
    }

    return {
        "regime": regime_label,
        "confidence": round(regime_confidence, 2),
        "regime_confidence": round(regime_confidence, 2),
        "leaders": leaders,
        "leader_selected": list(leaders),
        "specialists_selected": [],
        "reasons": selected_reasons,
        "rejected_candidates": skipped_reasons,
        "token_budget": resolved.get("token_budget", DEFAULT_TOKEN_BUDGET),
        "latency_budget": resolved.get("latency_budget"),
        "max_specialists_per_cycle": resolved.get(
            "max_specialists_per_cycle", DEFAULT_MAX_SPECIALISTS_PER_CYCLE
        ),
        "leader_weights": leader_weights,
        "low_confidence_mode": low_confidence,
        "selected_reasons": selected_reasons,
        "skipped_reasons": skipped_reasons,
    }


def select_specialists(
    regime: str,
    task: str | None = None,
    router_config: dict[str, Any] | None = None,
) -> list[str]:
    return select_specialist_plan(regime, task=task, router_config=router_config)["selected"]
