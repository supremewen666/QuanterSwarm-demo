"""API routes."""

from fastapi import APIRouter

from quanter_swarm.adapters.api.schemas import (
    BatchDataRequest,
    BatchDataResponse,
    BatchResearchResponse,
    HealthResponse,
    ProviderCatalogResponse,
    ResearchRequest,
    ResearchResponse,
)
from quanter_swarm.application import (
    FetchFundamentalsBatch,
    FetchMacroBatch,
    GetProviderTopology,
    RunBatchResearch,
    RunResearchCycle,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/data/providers", response_model=ProviderCatalogResponse)
def data_providers() -> ProviderCatalogResponse:
    return ProviderCatalogResponse.model_validate(GetProviderTopology().execute())


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    target_symbol = request.symbol or (request.symbols or ["AAPL"])[0]
    result = RunResearchCycle().execute(symbol=target_symbol, data_provider=request.data_provider)
    result["regime"] = result["active_regime"]
    return ResearchResponse.model_validate(result)


@router.post("/research/batch", response_model=BatchResearchResponse)
def research_batch(request: ResearchRequest) -> BatchResearchResponse:
    symbols = request.symbols or ([request.symbol] if request.symbol else [])
    results = []
    for result in RunBatchResearch().execute(symbols=symbols, data_provider=request.data_provider):
        result["regime"] = result["active_regime"]
        results.append(ResearchResponse.model_validate(result))
    return BatchResearchResponse(results=results)


@router.post("/data/fundamentals/batch", response_model=BatchDataResponse)
def batch_fundamentals(request: BatchDataRequest) -> BatchDataResponse:
    return BatchDataResponse.model_validate(
        FetchFundamentalsBatch().execute(symbols=request.symbols, data_provider=request.data_provider)
    )


@router.post("/data/macro/batch", response_model=BatchDataResponse)
def batch_macro(request: BatchDataRequest) -> BatchDataResponse:
    return BatchDataResponse.model_validate(
        FetchMacroBatch().execute(symbols=request.symbols, data_provider=request.data_provider)
    )
