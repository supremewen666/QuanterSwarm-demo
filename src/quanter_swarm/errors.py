"""Project-specific exception hierarchy."""


class QuanterSwarmError(Exception):
    """Base error for the project."""


class RouterError(QuanterSwarmError):
    """Raised when routing or routing configuration is invalid."""


class AgentExecutionError(QuanterSwarmError):
    """Raised when an agent fails to execute or breaks its contract."""


class DataProviderError(QuanterSwarmError):
    """Raised when data or config payloads cannot be loaded safely."""


class RiskGuardrailError(QuanterSwarmError):
    """Raised when risk validation fails."""


class BacktestError(QuanterSwarmError):
    """Raised when backtest or experiment execution cannot proceed."""
