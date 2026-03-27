# Example Cycle Output

This example shows the layered runtime shape expected after the architecture refactor.

```json
{
  "architecture_summary": {
    "control_plane": {
      "flow": ["orchestrator", "router", "leader", "specialist"],
      "orchestrator": {
        "name": "RootAgent",
        "state_sequence": ["bootstrap", "route", "lead", "rank", "risk", "report"]
      },
      "router": {
        "regime": "trend_up",
        "selected_leaders": ["momentum"],
        "selected_specialists": ["data_fetch", "sentiment"],
        "rejected_candidates": ["mean_reversion"],
        "routing_reasons": {
          "momentum": "regime_fit_high",
          "data_fetch": "required_bootstrap_context"
        }
      },
      "leaders": [
        {
          "name": "momentum",
          "proposal_score": 0.78,
          "posterior_score": 0.82,
          "used_specialists": ["data_fetch", "sentiment"]
        }
      ],
      "specialists": [
        {"name": "data_fetch", "role": "shared_specialist"},
        {"name": "sentiment", "role": "shared_specialist"}
      ]
    },
    "system_services": {
      "snapshot": {"status": "ok", "provider": "deterministic"},
      "ranking": {"status": "ok", "signal_count": 3},
      "risk": {"status": "pass", "approved": true},
      "portfolio": {"status": "vol_aware", "gross_exposure": 0.82},
      "execution": {"status": "executed", "action_count": 2},
      "reporting": {"status": "generated"}
    }
  }
}
```

The key point is that agents and services are now visible as separate layers in the exported runtime artifact.
