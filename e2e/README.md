# RNApdbee E2E Tests

## What this covers
- API-level end-to-end tests against the backend engine flows (3D, 2D, multi).
- Reuses frontend example files and parameter options.

## Requirements
- Python 3.9+
- Running stack: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`

## Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r e2e/requirements.txt
```

## Run
```
pytest e2e
```

## PDB Report Script
Generate a success/failure report for PDB ids and/or file paths.

Examples:
```
python -m e2e.pdb_report --pdb-id 1EHZ --pdb-id 2Z74
python -m e2e.pdb_report --pdb-ids "1EHZ,2Z74" --report-path e2e/pdb-report.json
python -m e2e.pdb_report --pdb-id-file e2e/pdb-ids.txt
python -m e2e.pdb_report --file /path/to/1EHZ.cif --file /path/to/2Z74.cif
```

Options:
- `--endpoint` (`2d`, `3d`, `multi`) default `3d`
- `--base-url` override backend base URL
- `--report-path` override report path
- `--fail-on-error/--no-fail-on-error` control exit code

## Configuration
- `RNAPDBEE_E2E_BASE_URL` (default `http://localhost/api/v1/engine`)
- `RNAPDBEE_E2E_PDB_ID` (default `1EHZ`)
- `RNAPDBEE_E2E_PDB_IDS` (comma-separated list, optional)
- `RNAPDBEE_E2E_INVALID_PDB_ID` (default `BAD`)
- `RNAPDBEE_E2E_PDB_ALLOW_FAILURES` (default `false`, set true to not fail on batch failures)
- `RNAPDBEE_E2E_REPORT_PATH` (default `e2e/pdb-report.json`)
