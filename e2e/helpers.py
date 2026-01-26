import os
import time
from typing import Any, Dict, Optional

import requests


DEFAULT_BASE_URL = "http://localhost/api/v1/engine"
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_POLL_INTERVAL_SECONDS = 2


def get_base_url() -> str:
    return os.getenv("RNAPDBEE_E2E_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_pdb_id() -> str:
    return os.getenv("RNAPDBEE_E2E_PDB_ID", "1EHZ")


def get_pdb_ids() -> list[str]:
    raw = os.getenv("RNAPDBEE_E2E_PDB_IDS")
    if not raw:
        return [get_pdb_id()]
    return [item.strip() for item in raw.split(",") if item.strip()]


def get_invalid_pdb_id() -> str:
    return os.getenv("RNAPDBEE_E2E_INVALID_PDB_ID", "BAD")


def allow_pdb_failures() -> bool:
    return os.getenv("RNAPDBEE_E2E_PDB_ALLOW_FAILURES", "false").lower() in {"1", "true", "yes"}


def get_report_path() -> str:
    return os.getenv("RNAPDBEE_E2E_REPORT_PATH", os.path.join("e2e", "pdb-report.json"))


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def post_text_file(
    endpoint: str,
    params: Dict[str, Any],
    file_path: str,
    base_url: Optional[str] = None,
) -> requests.Response:
    url = _join_url(base_url or get_base_url(), endpoint)
    filename = os.path.basename(file_path)
    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename}\"",
        "Content-Type": "text/plain",
    }
    payload = load_text_file(file_path)
    return requests.post(url, params=params, headers=headers, data=payload, timeout=120)


def post_pdb(
    endpoint: str,
    pdb_id: str,
    params: Dict[str, Any],
    base_url: Optional[str] = None,
) -> requests.Response:
    url = _join_url(base_url or get_base_url(), f"{endpoint}/pdb/{pdb_id}")
    return requests.post(url, params=params, timeout=120)


def post_reanalyze(
    endpoint: str,
    result_id: str,
    params: Dict[str, Any],
    base_url: Optional[str] = None,
) -> requests.Response:
    url = _join_url(base_url or get_base_url(), f"{endpoint}/{result_id}")
    return requests.post(url, params=params, timeout=120)


def get_result(endpoint: str, result_id: str, base_url: Optional[str] = None) -> requests.Response:
    url = _join_url(base_url or get_base_url(), f"{endpoint}/{result_id}")
    return requests.get(url, timeout=60)


def wait_for_result(
    endpoint: str,
    result_id: str,
    base_url: Optional[str] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS,
) -> Dict[str, Any]:
    start = time.time()
    last_error = None
    while time.time() - start < timeout_seconds:
        response = get_result(endpoint, result_id, base_url=base_url)
        if response.status_code == 200:
            return response.json()
        last_error = response.text
        time.sleep(poll_interval_seconds)
    raise AssertionError(f"Result {result_id} not ready: {last_error}")


def assert_basic_result_shape(payload: Dict[str, Any]) -> None:
    assert "id" in payload
    assert "filename" in payload
    assert "results" in payload
    assert isinstance(payload["results"], list)
    assert payload["results"], "results array is empty"
    assert "params" in payload["results"][0]
    assert "output" in payload["results"][0]


def _join_url(base_url: str, endpoint: str) -> str:
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
