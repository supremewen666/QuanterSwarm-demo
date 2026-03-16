"""Explicit orchestration states for cycle execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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


@dataclass(slots=True)
class StageRecord:
    stage: CycleStage
    status: str
    detail: dict
