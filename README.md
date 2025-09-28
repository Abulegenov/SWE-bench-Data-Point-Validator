# SWE-bench Data Point Validator

A command-line tool for validating SWE-bench data points using the official SWE-bench evaluation harness. This tool ensures that patches in SWE-bench data points work correctly by running them through the official evaluation system.

## Features

- ✅ **Official Integration**: Uses `swebench.harness.run_evaluation` for authentic validation
- ✅ **Comprehensive Testing**: Validates both `FAIL_TO_PASS` and `PASS_TO_PASS` tests
- ✅ **Detailed Reporting**: Provides clear success/failure status with error messages
- ✅ **Timeout Handling**: Configurable timeouts to prevent hanging evaluations
- ✅ **Multiple Input Modes**: Validate specific files or entire directories
- ✅ **Rich Output**: Beautiful console output with progress bars and colored results
- ✅ **JSON Export**: Optional JSON output for programmatic use

## Installation

This project uses UV for dependency management. Make sure you have UV installed:

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Usage

### Basic Usage

```bash
# Validate all data points in the default data_points/ directory
uv run python -m swe_bench_validator

# Or use the convenience script
./scripts/validate_swe_bench.sh
```

### Advanced Usage

```bash
# Validate specific files
uv run python -m swe_bench_validator --file data_points/astropy__astropy-11693.json

# Validate with custom timeout and verbose output
uv run python -m swe_bench_validator --timeout 600 --verbose

# Validate all files in a custom directory
uv run python -m swe_bench_validator --data-points-dir /path/to/data_points

# Output results in JSON format
uv run python -m swe_bench_validator --output-format json
```

### Command Line Options

- `--data-points-dir`: Directory containing data point JSON files (default: `data_points`)
- `--file`: Specific files to validate (can be used multiple times)
- `--timeout`: Timeout in seconds for each validation (default: 300)
- `--verbose`: Enable verbose output
- `--output-format`: Output format - `text` or `json` (default: `text`)

## How It Works

### Validation Process

1. **Load Data Point**: Reads and validates the JSON file structure
2. **Convert Format**: Converts SWE-bench data point to prediction format
3. **Run Evaluation**: Uses `swebench.harness.run_evaluation` to test the patch
4. **Check Results**: Verifies that:
   - Patch applies successfully
   - `FAIL_TO_PASS` tests now pass
   - `PASS_TO_PASS` tests still pass
5. **Report Results**: Provides detailed success/failure information

### Data Point Structure

The validator expects SWE-bench data points with these required fields:

```json
{
  "instance_id": "repo__repo-12345",
  "repo": "owner/repo",
  "base_commit": "abc123...",
  "patch": "diff --git a/...",
  "FAIL_TO_PASS": "[\"test_file::test_function\"]",
  "PASS_TO_PASS": "[\"test_file::test_function\"]",
  "problem_statement": "...",
  "hints_text": "..."
}
```

## Example Output

### Successful Validation

```
✓ astropy__astropy-11693: PASSED
✓ django__django-12345: PASSED

Validation Summary
• Total files: 2
• Validated: 2
• Successful: 2
• Failed: 0
• Errors: 0
```

### Failed Validation

```
✗ astropy__astropy-11693-fail: FAILED - FAIL_TO_PASS tests failed: Test execution error
✗ django__django-12345: FAILED - Patch failed to apply

Validation Summary
• Total files: 2
• Validated: 2
• Successful: 0
• Failed: 2
• Errors: 2
```

## Integration with GitHub Actions

This validator is designed to work with GitHub Actions for automated validation of data points in pull requests. See `.github/workflows/validate-datapoints.yml` for the workflow configuration.

## Error Handling

The validator handles various types of errors:

- **JSON Parsing Errors**: Invalid JSON format in data point files
- **Missing Fields**: Required fields not present in data point
- **Patch Application Failures**: Patches that don't apply cleanly
- **Test Execution Failures**: Tests that fail to run or don't pass
- **Timeout Errors**: Evaluations that exceed the configured timeout
- **Docker Errors**: Issues with the underlying Docker evaluation system

## Development

### Project Structure

```
├── swe_bench_validator/          # Validator package
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # CLI entry point
│   ├── validator.py             # Core validation logic
│   └── cli.py                   # Command-line interface
├── swe_bench_downloader/        # Data point downloader
├── data_points/                 # Sample data points
├── scripts/                     # Convenience scripts
└── .github/workflows/           # GitHub Actions workflows
```

### Running Tests

```bash
# Test the validator with sample data points
uv run python test_validator.py
```

## Requirements

- Python 3.10+
- Docker (for SWE-bench evaluation)
- SWE-bench library (installed via UV)

## License

This project is part of the SWE-bench Data Point Validator assignment.
