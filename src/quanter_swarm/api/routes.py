"""API routes."""

from fastapi import APIRouter

from quanter_swarm.api.schemas import (
    BatchDataRequest,
    BatchDataResponse,
    BatchResearchResponse,
    HealthResponse,
    ProviderCatalogResponse,
    ResearchRequest,
    ResearchResponse,
)
from quanter_swarm.data import available_providers
from quanter_swarm.data.provider_factory import build_provider_from_config, describe_provider_config
from quanter_swarm.orchestrator.root_agent import RootAgent
from quanter_swarm.utils.config import load_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/data/providers", response_model=ProviderCatalogResponse)
def data_providers() -> ProviderCatalogResponse:
    settings = load_settings()
    provider = build_provider_from_config(settings.data_provider)
    return ProviderCatalogResponse(
        available=available_providers(),
        configured=describe_provider_config(settings.data_provider, provider),
    )


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    target_symbol = request.symbol or (request.symbols or ["AAPL"])[0]
    provider_override = {"provider": request.data_provider} if request.data_provider else None
    result = RootAgent().run_sync(symbol=target_symbol, provider_override=provider_override)
    result["regime"] = result["active_regime"]
    return ResearchResponse.model_validate(result)


@router.post("/research/batch", response_model=BatchResearchResponse)
def research_batch(request: ResearchRequest) -> BatchResearchResponse:
    symbols = request.symbols or ([request.symbol] if request.symbol else [])
    results = []
    provider_override = {"provider": request.data_provider} if request.data_provider else None
    for result in RootAgent().run_batch_sync(symbols=symbols, provider_override=provider_override):
        result["regime"] = result["active_regime"]
        results.append(ResearchResponse.model_validate(result))
    return BatchResearchResponse(results=results)


@router.post("/data/fundamentals/batch", response_model=BatchDataResponse)
def batch_fundamentals(request: BatchDataRequest) -> BatchDataResponse:
    provider_config = {"provider": request.data_provider} if request.data_provider else {}
    provider = build_provider_from_config(provider_config)
    results = provider.get_fundamentals_batch(request.symbols)
    return BatchDataResponse(provider=getattr(provider, "data_source", provider.__class__.__name__), results=results)


@router.post("/data/macro/batch", response_model=BatchDataResponse)
def batch_macro(request: BatchDataRequest) -> BatchDataResponse:
    provider_config = {"provider": request.data_provider} if request.data_provider else {}
    provider = build_provider_from_config(provider_config)
    results = provider.get_macro_batch(request.symbols)
    return BatchDataResponse(provider=getattr(provider, "data_source", provider.__class__.__name__), results=results)
