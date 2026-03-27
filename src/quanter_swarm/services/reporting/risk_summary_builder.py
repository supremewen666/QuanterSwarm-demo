"""Risk summary builder."""


def build_risk_summary(warnings: list[str]) -> dict:
    return {"warnings": warnings, "status": "alert" if warnings else "clear"}
