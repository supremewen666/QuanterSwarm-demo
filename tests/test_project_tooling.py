import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_core_tooling() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    optional_deps = pyproject["project"]["optional-dependencies"]["dev"]
    assert any(dep.startswith("pytest") for dep in optional_deps)
    assert any(dep.startswith("ruff") for dep in optional_deps)
    assert any(dep.startswith("mypy") for dep in optional_deps)

    assert "tool" in pyproject
    assert "pytest" in pyproject["tool"]
    assert "ruff" in pyproject["tool"]
    assert "mypy" in pyproject["tool"]


def test_makefile_exposes_quality_targets() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text()

    for target in ("lint:", "test:", "typecheck:"):
        assert target in makefile

    assert "-m pytest" in makefile
    assert "-m ruff" in makefile
    assert "-m mypy" in makefile
