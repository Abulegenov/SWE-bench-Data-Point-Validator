#!/usr/bin/env python3
"""
Test script to verify the GitHub Action workflow structure and validator integration.
"""

import yaml
from pathlib import Path
from rich.console import Console

console = Console()


def test_workflow_structure():
    """Test that the GitHub Action workflow has the correct structure."""
    console.print("[bold blue]Testing GitHub Action Workflow Structure[/bold blue]")
    
    workflow_path = Path(".github/workflows/validate-datapoints.yml")
    
    if not workflow_path.exists():
        console.print("[red]❌ Workflow file not found[/red]")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ['name', 'on', 'jobs']
        for field in required_fields:
            if field not in workflow:
                console.print(f"[red]❌ Missing required field: {field}[/red]")
                return False
        
        # Check triggers
        triggers = workflow['on']
        if 'push' not in triggers or 'pull_request' not in triggers:
            console.print("[red]❌ Missing required triggers (push, pull_request)[/red]")
            return False
        
        # Check paths filter
        push_paths = triggers['push'].get('paths', [])
        pr_paths = triggers['pull_request'].get('paths', [])
        
        if 'data_points/**' not in push_paths or 'data_points/**' not in pr_paths:
            console.print("[red]❌ Missing data_points/** path filter[/red]")
            return False
        
        # Check job structure
        jobs = workflow['jobs']
        if 'validate-datapoints' not in jobs:
            console.print("[red]❌ Missing validate-datapoints job[/red]")
            return False
        
        job = jobs['validate-datapoints']
        if 'runs-on' not in job or 'steps' not in job:
            console.print("[red]❌ Missing required job fields[/red]")
            return False
        
        # Check steps
        steps = job['steps']
        step_names = [step['name'] for step in steps]
        
        required_steps = [
            'Checkout repository',
            'Set up Python',
            'Install UV',
            'Install dependencies',
            'Detect changed data point files',
            'Validate changed data points',
            'Run full validation (if no specific files changed)',
        ]
        
        for step_name in required_steps:
            if step_name not in step_names:
                console.print(f"[red]❌ Missing required step: {step_name}[/red]")
                return False
        
        console.print("[green]✅ Workflow structure is correct[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error parsing workflow: {e}[/red]")
        return False


def test_validator_integration():
    """Test that the validator can be imported and used."""
    console.print("\n[bold blue]Testing Validator Integration[/bold blue]")
    
    try:
        from swe_bench_validator import SWEBenchValidator
        from swe_bench_validator.cli import main
        
        # Test validator initialization
        validator = SWEBenchValidator(
            data_points_dir=Path("data_points"),
            timeout_per_instance=60,
            verbose=False,
        )
        
        console.print("[green]✅ Validator imports and initializes correctly[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Validator integration error: {e}[/red]")
        return False


def test_file_structure():
    """Test that all required files exist."""
    console.print("\n[bold blue]Testing File Structure[/bold blue]")
    
    required_files = [
        "swe_bench_validator/__init__.py",
        "swe_bench_validator/__main__.py", 
        "swe_bench_validator/validator.py",
        "swe_bench_validator/cli.py",
        ".github/workflows/validate-datapoints.yml",
        "scripts/validate_swe_bench.sh",
        "README.md",
        "swe-bench-docker-architecture.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            console.print(f"[green]✅ {file_path}[/green]")
        else:
            console.print(f"[red]❌ {file_path}[/red]")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    console.print("[bold]GitHub Action Workflow Test Suite[/bold]\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Workflow Structure", test_workflow_structure),
        ("Validator Integration", test_validator_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]❌ {test_name} failed with exception: {e}[/red]")
            results.append((test_name, False))
    
    # Summary
    console.print("\n[bold]Test Summary:[/bold]")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        console.print(f"{test_name}: {status}")
    
    console.print(f"\n[bold]Overall: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("[green]🎉 All tests passed! The workflow is ready.[/green]")
        return True
    else:
        console.print("[red]❌ Some tests failed. Please fix the issues.[/red]")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
