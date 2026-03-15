"""Base leader."""


class BaseLeader:
    name = "base"

    def propose(self, context: dict) -> dict:
        return {"leader": self.name, "symbol": context["symbol"], "score": 0.0, "thesis": "neutral"}
