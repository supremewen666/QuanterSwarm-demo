"""API schemas."""

from pydantic import BaseModel, Field

from quanter_swarm.contracts import CycleReport, ResearchRequestContract


class HealthResponse(BaseModel):
    status: str


class ResearchRequest(ResearchRequestContract):
    """Typed API request contract for research endpoints."""


class ResearchResponse(CycleReport):
    regime: str


class BatchResearchResponse(BaseModel):
    results: list[ResearchResponse]


class BatchDataRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=50)
    data_provider: str | None = None


class BatchDataResponse(BaseModel):
    provider: str
    results: dict


class ProviderCatalogResponse(BaseModel):
    available: list[str]
    configured: dict
