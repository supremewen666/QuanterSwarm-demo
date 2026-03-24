"""Bootstrap package so `python -m app...` works from the repository root."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
_SRC_APP = Path(__file__).resolve().parent.parent / "src" / "app"
if _SRC_ROOT.exists():
    src_root = str(_SRC_ROOT)
    if src_root not in sys.path:
        sys.path.insert(0, src_root)
if _SRC_APP.exists():
    __path__.append(str(_SRC_APP))
