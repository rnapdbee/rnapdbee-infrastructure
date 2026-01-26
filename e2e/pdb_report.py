import argparse
import json
import os
import sys
from typing import Any, Dict, List

from . import helpers


DEFAULTS = {
    "modelSelection": "FIRST",
    "analysisTool": "RNAPOLIS",
    "nonCanonicalHandling": "VISUALIZATION_ONLY",
    "removeIsolated": "false",
    "structuralElementsHandling": "USE_PSEUDOKNOTS",
    "visualizationTool": "VARNA",
    "includeNonCanonical": "false",
}


def main() -> int:
    args = parse_args()
    base_url = args.base_url or helpers.get_base_url()
    report_path = args.report_path or helpers.get_report_path()

    pdb_ids = collect_pdb_ids(args)
    file_paths = collect_file_paths(args)
    if not pdb_ids and not file_paths:
        print("No PDB ids or file paths provided.")
        return 2

    params = build_params(args)
    results = run_requests(base_url, args.endpoint, params, pdb_ids, file_paths)
    write_report(report_path, results)

    print(f"Report written to {report_path}:")
    print(json.dumps(results, indent=2, sort_keys=True))

    if args.fail_on_error and results["failed"]:
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PDB processing report")
    parser.add_argument("--base-url", help="Backend base URL (default uses env)")
    parser.add_argument("--report-path", help="JSON report path")
    parser.add_argument("--endpoint", default="3d", choices=["2d", "3d", "multi"])
    parser.add_argument("--pdb-id", action="append", default=[], help="PDB id (repeatable)")
    parser.add_argument("--pdb-ids", help="Comma-separated PDB ids")
    parser.add_argument("--pdb-id-file", help="File with one PDB id per line")
    parser.add_argument("--file", action="append", default=[], help="Path to PDB/mmCIF file (repeatable)")
    parser.add_argument("--fail-on-error", action=argparse.BooleanOptionalAction, default=True)

    parser.add_argument("--model-selection", default=DEFAULTS["modelSelection"])
    parser.add_argument("--analysis-tool", default=DEFAULTS["analysisTool"])
    parser.add_argument("--non-canonical-handling", default=DEFAULTS["nonCanonicalHandling"])
    parser.add_argument("--remove-isolated", default=DEFAULTS["removeIsolated"])
    parser.add_argument("--structural-elements-handling", default=DEFAULTS["structuralElementsHandling"])
    parser.add_argument("--visualization-tool", default=DEFAULTS["visualizationTool"])
    parser.add_argument("--include-non-canonical", default=DEFAULTS["includeNonCanonical"])

    return parser.parse_args()


def collect_pdb_ids(args: argparse.Namespace) -> List[str]:
    pdb_ids = list(args.pdb_id)
    if args.pdb_ids:
        pdb_ids.extend([item.strip() for item in args.pdb_ids.split(",") if item.strip()])
    if args.pdb_id_file:
        with open(args.pdb_id_file, "r", encoding="utf-8") as handle:
            for line in handle:
                item = line.strip()
                if item:
                    pdb_ids.append(item)
    return pdb_ids


def collect_file_paths(args: argparse.Namespace) -> List[str]:
    return list(args.file)


def build_params(args: argparse.Namespace) -> Dict[str, Any]:
    if args.endpoint == "2d":
        return {
            "removeIsolated": args.remove_isolated,
            "structuralElementsHandling": args.structural_elements_handling,
            "visualizationTool": args.visualization_tool,
        }
    if args.endpoint == "multi":
        return {
            "includeNonCanonical": args.include_non_canonical,
            "removeIsolated": args.remove_isolated,
            "visualizationTool": args.visualization_tool,
        }
    return {
        "modelSelection": args.model_selection,
        "analysisTool": args.analysis_tool,
        "nonCanonicalHandling": args.non_canonical_handling,
        "removeIsolated": args.remove_isolated,
        "structuralElementsHandling": args.structural_elements_handling,
        "visualizationTool": args.visualization_tool,
    }


def run_requests(
    base_url: str,
    endpoint: str,
    params: Dict[str, Any],
    pdb_ids: List[str],
    file_paths: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    results: Dict[str, List[Dict[str, Any]]] = {"success": [], "failed": []}

    for pdb_id in pdb_ids:
        response = helpers.post_pdb(endpoint, pdb_id, params, base_url=base_url)
        record = {
            "kind": "pdb_id",
            "id": pdb_id,
            "status": response.status_code,
        }
        store_result(results, record, response)

    for path in file_paths:
        response = helpers.post_text_file(endpoint, params, path, base_url=base_url)
        record = {
            "kind": "file",
            "path": path,
            "status": response.status_code,
        }
        store_result(results, record, response)

    return results


def store_result(
    results: Dict[str, List[Dict[str, Any]]],
    record: Dict[str, Any],
    response: Any,
) -> None:
    if response.status_code == 200:
        results["success"].append(record)
        return

    error_text = response.text
    record["error"] = error_text[:500] if error_text else ""
    results["failed"].append(record)


def write_report(path: str, results: Dict[str, Any]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    sys.exit(main())
