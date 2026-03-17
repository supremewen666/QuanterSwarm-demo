"""API routes."""

from fastapi import APIRouter

from quanter_swarm.api.schemas import (
    BatchResearchResponse,
    HealthResponse,
    ResearchRequest,
    ResearchResponse,
)
from quanter_swarm.orchestrator.root_agent import RootAgent

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    target_symbol = request.symbol or (request.symbols or ["AAPL"])[0]
    result = RootAgent().run_sync(symbol=target_symbol)
    result["regime"] = result["active_regime"]
    return ResearchResponse.model_validate(result)


@router.post("/research/batch", response_model=BatchResearchResponse)
def research_batch(request: ResearchRequest) -> BatchResearchResponse:
    symbols = request.symbols or ([request.symbol] if request.symbol else [])
    results = []
    for symbol in symbols:
        result = RootAgent().run_sync(symbol=symbol)
        result["regime"] = result["active_regime"]
        results.append(ResearchResponse.model_validate(result))
    return BatchResearchResponse(results=results)
