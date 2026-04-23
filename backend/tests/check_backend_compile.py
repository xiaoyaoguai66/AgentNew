from __future__ import annotations

import compileall
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = [
    "cache",
    "config",
    "crud",
    "models",
    "prompts",
    "routers",
    "schemas",
    "services",
    "tasks",
    "tests",
    "utils",
]


def run_compile_checks() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ROOT / "main.py"), doraise=True)
    except py_compile.PyCompileError as exc:
        failures.append(f"main.py: {exc.msg}")

    for directory in SOURCE_DIRS:
        path = ROOT / directory
        if not path.exists():
            continue
        ok = compileall.compile_dir(
            str(path),
            quiet=1,
            force=False,
        )
        if not ok:
            failures.append(directory)

    if failures:
        raise SystemExit(
            "Backend compile checks failed:\n- " + "\n- ".join(failures)
        )


if __name__ == "__main__":
    run_compile_checks()
    print("Backend targeted compile checks passed.")
