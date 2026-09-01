"""Verify that an sdist is self-contained and can produce an installable wheel."""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REQUIRED_SUFFIXES = (
    "/pyproject.toml",
    "/README.md",
    "/LICENSE",
    "/__init__.py",
    "/tests/test_nanoyaml.py",
    "/tools/check_wheel.py",
)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_sdist.py SDIST")
    sdist = Path(sys.argv[1]).resolve()
    with tarfile.open(sdist, "r:gz") as archive:
        names = archive.getnames()
        missing = [
            suffix
            for suffix in REQUIRED_SUFFIXES
            if not any(name.endswith(suffix) for name in names)
        ]
        if missing:
            raise SystemExit(f"sdist is missing: {', '.join(missing)}")
        with tempfile.TemporaryDirectory() as temporary:
            archive.extractall(temporary)
            roots = [Path(temporary) / name for name in names if "/" not in name]
            root = next((path for path in roots if path.is_dir()), None)
            if root is None:
                raise SystemExit("sdist has no top-level source directory")
            wheel_dir = Path(temporary) / "wheel"
            wheel_dir.mkdir()
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    str(root),
                    "--no-deps",
                    "--wheel-dir",
                    str(wheel_dir),
                ],
                check=True,
            )
            wheels = list(wheel_dir.glob("*.whl"))
            if len(wheels) != 1:
                raise SystemExit("sdist did not produce exactly one wheel")
            subprocess.run(
                [
                    sys.executable,
                    str(root / "tools" / "check_wheel.py"),
                    str(wheels[0]),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
