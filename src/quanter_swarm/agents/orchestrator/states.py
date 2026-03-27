"""Explicit orchestration states for cycle execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CycleState(StrEnum):
    INIT = "init"
    DATA_FETCH = "data_fetch"
    REGIME_DETECT = "regime_detect"
    ROUTING = "routing"
    AGENT_EXECUTION = "agent_execution"
    PORTFOLIO_BUILD = "portfolio_build"
    RISK_CHECK = "risk_check"
    REPORT_GENERATION = "report_generation"
    DONE = "done"
    FAILED = "failed"


class CycleStage(StrEnum):
    INGEST = "ingest"
    REGIME = "regime"
    ROUTE = "route"
    SPECIALIST_RESEARCH = "specialist_research"
    LEADER_PROPOSAL = "leader_proposal"
    RANK = "rank"
    RISK = "risk"
    ALLOCATE = "allocate"
    EXECUTE = "execute"
    REPORT = "report"


_STAGE_TO_STATE: dict[CycleStage, CycleState] = {
    CycleStage.INGEST: CycleState.DATA_FETCH,
    CycleStage.REGIME: CycleState.REGIME_DETECT,
    CycleStage.ROUTE: CycleState.ROUTING,
    CycleStage.SPECIALIST_RESEARCH: CycleState.AGENT_EXECUTION,
    CycleStage.LEADER_PROPOSAL: CycleState.AGENT_EXECUTION,
    CycleStage.RANK: CycleState.AGENT_EXECUTION,
    CycleStage.RISK: CycleState.RISK_CHECK,
    CycleStage.ALLOCATE: CycleState.PORTFOLIO_BUILD,
    CycleStage.EXECUTE: CycleState.AGENT_EXECUTION,
    CycleStage.REPORT: CycleState.REPORT_GENERATION,
}


def state_for_stage(stage: CycleStage) -> CycleState:
    return _STAGE_TO_STATE[stage]


@dataclass(slots=True)
class StageRecord:
    stage: CycleStage
    status: str
    detail: dict
    state: CycleState = field(init=False)

    def __post_init__(self) -> None:
        self.state = state_for_stage(self.stage)
