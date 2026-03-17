"""API schemas."""

from pydantic import BaseModel

from quanter_swarm.contracts import CycleReport, ResearchRequestContract


class HealthResponse(BaseModel):
    status: str


class ResearchRequest(ResearchRequestContract):
    pass


class ResearchResponse(CycleReport):
    regime: str


class BatchResearchResponse(BaseModel):
    results: list[ResearchResponse]
