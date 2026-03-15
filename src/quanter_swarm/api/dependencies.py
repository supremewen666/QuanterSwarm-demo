"""API dependency placeholders."""

from quanter_swarm.settings import Settings


def get_settings() -> Settings:
    return Settings()
