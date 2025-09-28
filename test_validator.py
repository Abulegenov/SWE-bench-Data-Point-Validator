#!/usr/bin/env python3
"""
Test script for the SWE-bench validator.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from swe_bench_validator import SWEBenchValidator
from rich.console import Console

console = Console()


def test_validator():
    """Test the validator with sample data points."""
    console.print("[bold blue]Testing SWE-bench Validator[/bold blue]")
    
    # Initialize validator
    validator = SWEBenchValidator(
        data_points_dir=Path("data_points"),
        timeout_per_instance=60,  # Shorter timeout for testing
        verbose=True,
    )
    
    # Test with sample files
    sample_files = [
        Path("data_points/astropy__astropy-11693.json"),
        Path("data_points/astropy__astropy-11693-fail.json"),
    ]
    
    console.print(f"[yellow]Testing with {len(sample_files)} sample files...[/yellow]")
    
    # Validate specific files
    results = validator.validate_specific_files(sample_files)
    
    # Display results
    console.print("\n[bold]Test Results:[/bold]")
    console.print(f"Total files: {results['total_files']}")
    console.print(f"Successful: {results['successful']}")
    console.print(f"Failed: {results['failed']}")
    console.print(f"Errors: {results['errors']}")
    
    # Show individual results
    for result in results['results']:
        status = "✓ PASS" if result.success else "✗ FAIL"
        console.print(f"{result.instance_id}: {status}")
        if result.error_message:
            console.print(f"  Error: {result.error_message}")
    
    return results


if __name__ == "__main__":
    try:
        results = test_validator()
        
        # Exit with appropriate code
        if results["errors"] > 0:
            console.print("[red]Test completed with errors[/red]")
            sys.exit(1)
        else:
            console.print("[green]Test completed successfully[/green]")
            sys.exit(0)
            
    except Exception as e:
        console.print(f"[red]Test failed with exception: {e}[/red]")
        console.print_exception()
        sys.exit(1)
