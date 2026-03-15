# Routing Rules

Route tasks by market regime, data freshness, token budget, and requested output type.

Router behavior:

- apply confidence threshold from `configs/router.yaml`
- when regime confidence is low, use configured fallback leaders or no-trade
- enforce `max_active_leaders`
- record selected and skipped reasons in decision trace
