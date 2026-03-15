"""API routes."""

from fastapi import APIRouter

from quanter_swarm.api.schemas import HealthResponse, ResearchRequest, ResearchResponse
from quanter_swarm.orchestrator.root_agent import RootAgent

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    return ResearchResponse.model_validate(RootAgent().run(symbol=request.symbol))
