import os
import json

from . import helpers


def test_tertiary_to_dbn_flow(base_url, examples_root):
    params = {
        "modelSelection": "FIRST",
        "analysisTool": "RNAPOLIS",
        "nonCanonicalHandling": "VISUALIZATION_ONLY",
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    file_path = os.path.join(examples_root, "tertiary", "1EHZ.cif")
    response = helpers.post_text_file("3d", params, file_path, base_url=base_url)
    assert response.status_code == 200
    payload = response.json()
    helpers.assert_basic_result_shape(payload)
    result_id = payload["id"]

    fetched = helpers.wait_for_result("3d", result_id, base_url=base_url)
    helpers.assert_basic_result_shape(fetched)
    assert fetched["results"][0]["output"]["models"]


def test_secondary_to_dbn_flow(base_url, examples_root):
    params = {
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    file_path = os.path.join(examples_root, "secondary", "1EHZ.bpseq")
    response = helpers.post_text_file("2d", params, file_path, base_url=base_url)
    assert response.status_code == 200
    payload = response.json()
    helpers.assert_basic_result_shape(payload)
    output = payload["results"][0]["output"]
    assert output["strands"]
    assert output["bpSeq"]


def test_tertiary_to_multi_flow(base_url, examples_root):
    params = {
        "includeNonCanonical": "false",
        "removeIsolated": "false",
        "visualizationTool": "VARNA",
    }
    file_path = os.path.join(examples_root, "tertiary", "2Z74.cif")
    response = helpers.post_text_file("multi", params, file_path, base_url=base_url)
    assert response.status_code == 200
    payload = response.json()
    helpers.assert_basic_result_shape(payload)
    assert payload["results"][0]["output"]["entries"]


def test_reanalyze_with_new_params(base_url, examples_root):
    params = {
        "modelSelection": "FIRST",
        "analysisTool": "RNAPOLIS",
        "nonCanonicalHandling": "VISUALIZATION_ONLY",
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    file_path = os.path.join(examples_root, "tertiary", "3G78.cif")
    response = helpers.post_text_file("3d", params, file_path, base_url=base_url)
    assert response.status_code == 200
    payload = response.json()
    helpers.assert_basic_result_shape(payload)

    reanalyze_params = {
        "modelSelection": "ALL",
        "analysisTool": "FR3D_PYTHON",
        "nonCanonicalHandling": "TEXT_AND_VISUALIZATION",
        "removeIsolated": "true",
        "structuralElementsHandling": "IGNORE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    result_id = payload["id"]
    reanalyze = helpers.post_reanalyze("3d", result_id, reanalyze_params, base_url=base_url)
    assert reanalyze.status_code == 200
    updated = reanalyze.json()
    helpers.assert_basic_result_shape(updated)
    assert len(updated["results"]) >= 2


def test_pdb_calculation_configurable(base_url):
    params = {
        "modelSelection": "FIRST",
        "analysisTool": "RNAPOLIS",
        "nonCanonicalHandling": "VISUALIZATION_ONLY",
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    pdb_id = helpers.get_pdb_id()
    response = helpers.post_pdb("3d", pdb_id, params, base_url=base_url)
    assert response.status_code == 200
    payload = response.json()
    helpers.assert_basic_result_shape(payload)


def test_invalid_pdb_id_returns_error(base_url):
    params = {
        "modelSelection": "FIRST",
        "analysisTool": "RNAPOLIS",
        "nonCanonicalHandling": "VISUALIZATION_ONLY",
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    response = helpers.post_pdb("3d", helpers.get_invalid_pdb_id(), params, base_url=base_url)
    assert response.status_code >= 400


def test_pdb_id_batch_report(base_url):
    params = {
        "modelSelection": "FIRST",
        "analysisTool": "RNAPOLIS",
        "nonCanonicalHandling": "VISUALIZATION_ONLY",
        "removeIsolated": "false",
        "structuralElementsHandling": "USE_PSEUDOKNOTS",
        "visualizationTool": "VARNA",
    }
    results = {"success": [], "failed": []}
    for pdb_id in helpers.get_pdb_ids():
        response = helpers.post_pdb("3d", pdb_id, params, base_url=base_url)
        if response.status_code == 200:
            results["success"].append(pdb_id)
        else:
            results["failed"].append({"id": pdb_id, "status": response.status_code})

    report_path = helpers.get_report_path()
    report_dir = os.path.dirname(report_path)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)

    print(f"PDB report written to {report_path}:")
    print(json.dumps(results, indent=2, sort_keys=True))

    if results["failed"] and not helpers.allow_pdb_failures():
        failed_ids = ", ".join(item["id"] for item in results["failed"])
        raise AssertionError(f"PDB ids failed: {failed_ids}")
