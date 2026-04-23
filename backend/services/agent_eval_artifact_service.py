import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config.settings import PROJECT_ROOT


_write_lock = threading.Lock()
EVAL_DIR = PROJECT_ROOT / "backend" / "data" / "evals"
EVAL_RUNS_PATH = EVAL_DIR / "eval_runs.jsonl"
EVAL_FAILURES_PATH = EVAL_DIR / "eval_failures.jsonl"
RESPONSE_EVAL_RUNS_PATH = EVAL_DIR / "response_eval_runs.jsonl"
RESPONSE_EVAL_FAILURES_PATH = EVAL_DIR / "response_eval_failures.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dir() -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, record: dict) -> None:
    _ensure_dir()
    payload = json.dumps(record, ensure_ascii=False)
    with _write_lock:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")


def create_eval_run_context() -> dict:
    return {
        "runId": uuid4().hex,
        "recordedAt": _utc_now_iso(),
    }


def record_eval_run(summary: dict) -> None:
    _append_jsonl(EVAL_RUNS_PATH, summary)


def record_failure_cases(*, run_context: dict, results: list[dict]) -> None:
    for item in results:
        if not item.get("mismatches"):
            continue
        _append_jsonl(
            EVAL_FAILURES_PATH,
            {
                "runId": run_context["runId"],
                "recordedAt": run_context["recordedAt"],
                **item,
            },
        )


def _read_recent(path: Path, limit: int = 10) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records.reverse()
    return records[: max(limit, 1)]


def read_recent_eval_runs(limit: int = 10) -> list[dict]:
    return _read_recent(EVAL_RUNS_PATH, limit=limit)


def read_recent_failure_cases(limit: int = 10) -> list[dict]:
    return _read_recent(EVAL_FAILURES_PATH, limit=limit)


def record_response_eval_run(summary: dict) -> None:
    _append_jsonl(RESPONSE_EVAL_RUNS_PATH, summary)


def record_response_failure_cases(*, run_context: dict, results: list[dict]) -> None:
    for item in results:
        if not item.get("mismatches"):
            continue
        _append_jsonl(
            RESPONSE_EVAL_FAILURES_PATH,
            {
                "runId": run_context["runId"],
                "recordedAt": run_context["recordedAt"],
                **item,
            },
        )


def read_recent_response_eval_runs(limit: int = 10) -> list[dict]:
    return _read_recent(RESPONSE_EVAL_RUNS_PATH, limit=limit)


def read_recent_response_failure_cases(limit: int = 10) -> list[dict]:
    return _read_recent(RESPONSE_EVAL_FAILURES_PATH, limit=limit)


def get_runtime_status() -> dict:
    return {
        "evalArtifactsEnabled": True,
        "evalRunsPath": str(EVAL_RUNS_PATH),
        "evalFailuresPath": str(EVAL_FAILURES_PATH),
        "responseEvalRunsPath": str(RESPONSE_EVAL_RUNS_PATH),
        "responseEvalFailuresPath": str(RESPONSE_EVAL_FAILURES_PATH),
    }
