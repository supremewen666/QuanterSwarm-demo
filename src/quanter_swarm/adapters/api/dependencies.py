"""API dependency placeholders."""

from quanter_swarm.config.settings import Settings


def get_settings() -> Settings:
    return Settings()
