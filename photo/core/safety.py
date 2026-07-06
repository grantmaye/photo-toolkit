from __future__ import annotations

from pathlib import Path


class SafetyError(RuntimeError):
    """Raised when a command refuses an unsafe operation."""


def assert_safe_source(path: Path, allow_root_path: bool = False) -> None:
    resolved = Path(path).expanduser().resolve()
    if allow_root_path:
        return
    dangerous = {Path("/"), Path("/home"), Path("/mnt")}
    if resolved in dangerous or resolved.parent == resolved:
        raise SafetyError(
            f"Refusing to operate on dangerous path: {resolved}. "
            "Pass --allow-root-path only if you are certain."
        )
    anchor = Path(resolved.anchor)
    if resolved == anchor:
        raise SafetyError(
            f"Refusing to operate on drive root: {resolved}. "
            "Pass --allow-root-path only if you are certain."
        )


def assert_distinct_paths(source: Path, destination: Path) -> None:
    if Path(source).expanduser().resolve() == Path(destination).expanduser().resolve():
        raise SafetyError("Source and destination must be different paths.")


def require_execute(execute: bool, action: str) -> None:
    if not execute:
        return
    if not isinstance(execute, bool):
        raise SafetyError(f"Invalid execute value for {action}.")
