"""
Runtime cache helpers for tools that need writable filesystem state.
"""

import os
import tempfile
from pathlib import Path


def ensure_matplotlib_cache(cache_root: str | None = None) -> Path:
    """
    Point Matplotlib and XDG cache directories at a writable location.

    This avoids warnings and first-run failures when the default home
    directory is read-only or sandboxed.
    """
    base_dir = Path(cache_root) if cache_root else Path(tempfile.gettempdir()) / "rubicCubeThesis_cache"
    mpl_cache = base_dir / "matplotlib"
    xdg_cache = base_dir / "xdg"

    mpl_cache.mkdir(parents=True, exist_ok=True)
    xdg_cache.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache))
    return base_dir
