"""Fundamentals parser."""


def parse_fundamentals(raw_payload: dict) -> dict:
    valuation = raw_payload.get("valuation", 0.0)
    growth = raw_payload.get("growth", 0.0)
    quality = raw_payload.get("quality", 0.0)
    leverage = raw_payload.get("leverage", 0.0)
    xbrl_facts = list(raw_payload.get("xbrl_facts", []))
    sec_filings = list(raw_payload.get("sec_filings", []))
    revenue_facts = [row for row in xbrl_facts if row.get("metric_name") == "Revenues"]
    income_facts = [row for row in xbrl_facts if row.get("metric_name") == "NetIncomeLoss"]
    latest_revenue = float(revenue_facts[-1].get("metric_value", 0.0)) if revenue_facts else 0.0
    latest_income = float(income_facts[-1].get("metric_value", 0.0)) if income_facts else 0.0
    xbrl_quality_boost = 0.1 if xbrl_facts else 0.0
    return {
        "valuation_score": round(max(0.0, 1 - valuation / 4), 2),
        "growth_score": round(min(1.0, max(growth / 2, latest_revenue / max(1.0, latest_revenue + 1000)))), 
        "quality_score": round(min(1.0, quality / 2 + xbrl_quality_boost), 2),
        "leverage_penalty": round(leverage / 2, 2),
        "xbrl_fact_count": len(xbrl_facts),
        "filing_count": len(sec_filings),
        "filing_recency_score": 1.0 if sec_filings else 0.0,
        "net_income_signal": round(latest_income, 2),
    }
