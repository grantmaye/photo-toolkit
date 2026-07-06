from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_manifest(paths: list[Path]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in paths:
        rows.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return rows


def duplicate_groups(paths: list[Path]) -> dict[str, list[Path]]:
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        by_hash[sha256_file(path)].append(path)
    return {digest: group for digest, group in by_hash.items() if len(group) > 1}
