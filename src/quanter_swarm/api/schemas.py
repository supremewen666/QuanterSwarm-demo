"""API schemas."""

from pydantic import BaseModel

from quanter_swarm.contracts import FinalReportContract, ResearchRequestContract


class HealthResponse(BaseModel):
    status: str


class ResearchRequest(ResearchRequestContract):
    pass


class ResearchResponse(FinalReportContract):
    regime: str


class BatchResearchResponse(BaseModel):
    results: list[ResearchResponse]
