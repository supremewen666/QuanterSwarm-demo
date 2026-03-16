# Output Format

The system should emit machine-readable JSON packets for intermediate stages and concise markdown summaries for final reports.

Required user-facing fields:

- active regime and regime confidence
- active leaders
- factor scorecard
- risk alerts
- portfolio suggestion
- paper trade actions
- evaluation summary
- decision trace summary

Schema-first contracts are enforced in:

- `src/quanter_swarm/contracts.py`
- `shared/schemas/*.schema.json`
