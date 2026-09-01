"""Verify that a wheel contains and installs the real NanoYAML package."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_wheel.py WHEEL")
    wheel = Path(sys.argv[1]).resolve()
    with zipfile.ZipFile(wheel) as archive:
        if "nanoyaml/__init__.py" not in archive.namelist():
            raise SystemExit("wheel does not contain nanoyaml/__init__.py")

    with tempfile.TemporaryDirectory() as temporary:
        environment = Path(temporary) / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / "bin" / "python"
        subprocess.run(
            [python, "-m", "pip", "install", "--quiet", str(wheel)],
            check=True,
        )
        result = subprocess.run(
            [
                python,
                "-I",
                "-c",
                (
                    "import nanoyaml; "
                    "assert str(nanoyaml.__file__).startswith("
                    "__import__('sys').prefix); "
                    "value={'key': ['value', 1]}; "
                    "assert nanoyaml.loads(nanoyaml.dumps(value)) == value"
                ),
            ],
            cwd=temporary,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stderr:
            raise SystemExit(result.stderr)


if __name__ == "__main__":
    main()
