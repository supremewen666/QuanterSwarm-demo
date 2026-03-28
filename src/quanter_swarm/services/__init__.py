"""Stable package-level exports for non-agent system services."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "BaseDataProvider": ("quanter_swarm.services.data", "BaseDataProvider"),
    "ConfiguredExperimentRunner": ("quanter_swarm.services.backtest", "ConfiguredExperimentRunner"),
    "DeterministicDataProvider": ("quanter_swarm.services.data", "DeterministicDataProvider"),
    "EventMemoryStore": ("quanter_swarm.services.evolution", "EventMemoryStore"),
    "EvolutionAuditLog": ("quanter_swarm.services.evolution", "EvolutionAuditLog"),
    "EvolutionManager": ("quanter_swarm.services.evolution", "EvolutionManager"),
    "ExperimentRunner": ("quanter_swarm.services.backtest", "ExperimentRunner"),
    "LeaderRegistry": ("quanter_swarm.services.evolution", "LeaderRegistry"),
    "MemoryStore": ("quanter_swarm.services.memory", "MemoryStore"),
    "PromotionGate": ("quanter_swarm.services.evolution", "PromotionGate"),
    "analyze_event_impact": ("quanter_swarm.services.research", "analyze_event_impact"),
    "assess_guardrails": ("quanter_swarm.services.risk", "assess_guardrails"),
    "build_cycle_metrics": ("quanter_swarm.services.monitoring", "build_cycle_metrics"),
    "build_monitoring_from_report_dir": ("quanter_swarm.services.monitoring", "build_monitoring_from_report_dir"),
    "build_monitoring_snapshot": ("quanter_swarm.services.monitoring", "build_monitoring_snapshot"),
    "build_portfolio": ("quanter_swarm.services.portfolio", "build_portfolio"),
    "build_runtime_monitoring_snapshot": ("quanter_swarm.services.monitoring", "build_runtime_monitoring_snapshot"),
    "build_snapshot": ("quanter_swarm.services.snapshot", "build_snapshot"),
    "build_snapshots": ("quanter_swarm.services.snapshot", "build_snapshots"),
    "compress": ("quanter_swarm.services.memory", "compress"),
    "compute_factor_score": ("quanter_swarm.services.research", "compute_factor_score"),
    "estimate_token_cost": ("quanter_swarm.services.monitoring", "estimate_token_cost"),
    "evaluate_risk_rules": ("quanter_swarm.services.risk", "evaluate_risk_rules"),
    "execute": ("quanter_swarm.services.execution", "execute"),
    "execution_allowed": ("quanter_swarm.services.execution", "execution_allowed"),
    "generate_report": ("quanter_swarm.services.reporting", "generate_report"),
    "get_default_data_provider": ("quanter_swarm.services.data", "get_default_data_provider"),
    "optimize_weights": ("quanter_swarm.services.portfolio", "optimize_weights"),
    "parse_fundamentals": ("quanter_swarm.services.research", "parse_fundamentals"),
    "passes_guardrails": ("quanter_swarm.services.risk", "passes_guardrails"),
    "provider_for_mode": ("quanter_swarm.services.data", "provider_for_mode"),
    "rank_candidates": ("quanter_swarm.services.ranking", "rank_candidates"),
    "render_markdown_report": ("quanter_swarm.services.reporting", "render_markdown_report"),
    "retrieve": ("quanter_swarm.services.memory", "retrieve"),
    "size_order": ("quanter_swarm.services.portfolio", "size_order"),
    "summarize": ("quanter_swarm.services.memory", "summarize"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
