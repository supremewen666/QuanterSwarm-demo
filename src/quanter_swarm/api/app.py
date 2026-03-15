"""FastAPI application."""

from fastapi import FastAPI

from quanter_swarm.api.routes import router

app = FastAPI(title="QuanterSwarm")
app.include_router(router)
