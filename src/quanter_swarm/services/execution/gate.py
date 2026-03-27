"""Execution gate."""


def execution_allowed(mode: str = "paper") -> tuple[bool, str]:
    if mode == "paper":
        return True, "paper_mode_enabled"
    return False, "live_execution_blocked"
