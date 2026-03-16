# Skill Examples

## 1) Single-ticket research (normal)

Input:

```json
{"symbol":"AAPL","horizon":"1w","output_format":"json"}
```

Run:

```bash
python skill/quanter-swarm/scripts/run_skill_request.py --request-json '{"symbol":"AAPL","horizon":"1w","output_format":"json"}' --mode normal
```

Expected structure:

- regime + regime_confidence
- active_leaders
- thesis_summary
- factor_scorecard
- portfolio_suggestion
- decision_trace_summary

## 2) Multi-ticket ranking (first-ticket execution)

Input:

```json
{"symbols":["AAPL","MSFT","NVDA"],"portfolio_mode":"multi","horizon":"1w"}
```

Quality criteria:

- output schema remains stable
- first symbol report is valid and traceable

## 3) Degraded mode

Run:

```bash
python skill/quanter-swarm/scripts/run_skill_request.py --request-json '{"symbol":"NVDA"}' --mode degraded
```

Quality criteria:

- `decision_trace_summary.fallback_modes` includes specialist fallback
- no schema field is dropped

## 4) Missing-data mode

Run:

```bash
python skill/quanter-swarm/scripts/run_skill_request.py --request-json '{"symbol":"TSLA"}' --mode missing_data
```

Quality criteria:

- fallback modes include missing-data pathways
- report still returns valid risk and portfolio sections

## 5) No-trade mode

Run:

```bash
python skill/quanter-swarm/scripts/run_skill_request.py --request-json '{"symbol":"MSFT"}' --mode no_trade
```

Quality criteria:

- `portfolio_suggestion.mode = no_trade`
- `paper_trade_actions` may be empty
- diagnostics remain available
