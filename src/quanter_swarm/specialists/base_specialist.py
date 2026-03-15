"""Base specialist."""


class BaseSpecialist:
    name = "base"

    def run(self, payload: dict) -> dict:
        return {"specialist": self.name, "payload": payload}
