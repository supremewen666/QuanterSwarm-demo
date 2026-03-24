"""Dashboard ASGI app."""

from app.services.dashboard_service import create_dashboard_app

app = create_dashboard_app()
