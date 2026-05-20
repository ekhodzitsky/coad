from __future__ import annotations

from pathlib import Path


def read_utf8(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeError:
        return None, "could not be read as UTF-8"
    except OSError as exc:
        detail = exc.strerror or str(exc)
        return None, f"could not be read: {detail}"
