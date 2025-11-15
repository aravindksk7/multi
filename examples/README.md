# Example XML Files

This directory contains sample XML files for testing the comparison functionality.

## Files

- **baseline.xml**: Baseline test report with 10 passing tests
- **current.xml**: Current test report with 11 tests (2 failures, 1 new test)

## Differences Between baseline.xml and current.xml

### Summary
- **Tests count**: 10 → 11 (1 added)
- **Failures**: 0 → 2 (2 new failures)
- **Total time**: 45.678s → 52.456s

### Detailed Changes

1. **Test Suite Attributes**
   - `tests`: 10 → 11
   - `failures`: 0 → 2
   - `time`: 45.678 → 52.456
   - `timestamp`: Updated

2. **Properties**
   - New property added: `version="2.0"`

3. **Test Case Changes**
   - `test_user_login`: Time changed (2.345 → 2.567)
   - `test_user_logout`: **Status changed from pass to fail** with failure message
   - `test_profile_update`: Time changed (4.567 → 5.012)
   - `test_create_item`: Time changed (5.678 → 6.234)
   - `test_update_item`: **Status changed from pass to fail** with failure message
   - `test_search_functionality`: Time changed (6.789 → 7.890)
   - `test_filter_results`: Time changed (4.321 → 5.678)

4. **New Test**
   - `test_export_data`: New test case added (passing)

## Usage

### Web UI
1. Go to http://localhost:8000/compare/new
2. Copy contents of `baseline.xml` into "Baseline XML" field
3. Copy contents of `current.xml` into "Current XML" field
4. Add metadata:
   - Suite Name: E2E Test Suite
   - Environment: staging
   - Run ID: run-001
5. Click "Compare XMLs"

### REST API
```powershell
# Read XML files
$baseline = Get-Content examples/baseline.xml -Raw
$current = Get-Content examples/current.xml -Raw

# Create comparison job
$body = @{
    baseline_xml = $baseline
    current_xml = $current
    suite_name = "E2E Test Suite"
    environment = "staging"
    run_id = "run-001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/xml-compare/jobs" -Method Post -Body $body -ContentType "application/json"
```

### Using curl
```bash
curl -X POST "http://localhost:8000/api/xml-compare/jobs" \
  -H "Content-Type: application/json" \
  -d @- << EOF
{
  "baseline_xml": "$(cat examples/baseline.xml | sed 's/"/\\"/g' | tr -d '\n')",
  "current_xml": "$(cat examples/current.xml | sed 's/"/\\"/g' | tr -d '\n')",
  "suite_name": "E2E Test Suite",
  "environment": "staging",
  "run_id": "run-001"
}
EOF
```
