"""Risk specialist."""

from __future__ import annotations

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class RiskSpecialist(BaseSpecialist):
    name = "risk"

    def assess(self, proposal: dict) -> dict:
        warnings: list[str] = []
        volatility = float(proposal.get("volatility", 0.0))
        macro_risk = float(proposal.get("macro_risk", 0.0))

        if volatility > 0.06:
            warnings.append("high_volatility")
        if macro_risk >= 0.8:
            warnings.append("elevated_macro_risk")

        return {
            "approved": not warnings,
            "warnings": warnings,
            "proposal": proposal,
        }
