"""Dashboard ASGI app."""

from quanter_swarm.application.task_flows import create_dashboard_app

app = create_dashboard_app()
