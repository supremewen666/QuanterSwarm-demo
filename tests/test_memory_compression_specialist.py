from quanter_swarm.agents.specialists.memory_compression_specialist import (
    MemoryCompressionSpecialist,
)


def test_memory_compression_specialist_marks_payload() -> None:
    assert MemoryCompressionSpecialist().compress({"x": 1})["compressed"] is True
