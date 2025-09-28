"""
Command-line interface for the SWE-bench data point validator.
"""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .validator import SWEBenchValidator

console = Console()


@click.command()
@click.option(
    "--data-points-dir",
    default="data_points",
    help="Directory containing data point JSON files (default: data_points)",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--file",
    "files",
    multiple=True,
    help="Specific files to validate (can be used multiple times)",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--timeout",
    default=300,
    help="Timeout in seconds for each validation (default: 300)",
    type=int,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
def main(data_points_dir, files, timeout, verbose, output_format):
    """
    Validate SWE-bench data points using the official evaluation harness.
    
    This tool validates that patches in SWE-bench data points work correctly
    by running them through the official SWE-bench evaluation system.
    
    Examples:
    
    # Validate all data points in the default directory
    python -m swe_bench_validator
    
    # Validate specific files
    python -m swe_bench_validator --file data_points/astropy__astropy-11693.json
    
    # Validate with custom timeout and verbose output
    python -m swe_bench_validator --timeout 600 --verbose
    
    # Validate all files in a custom directory
    python -m swe_bench_validator --data-points-dir /path/to/data_points
    """
    try:
        # Initialize validator
        validator = SWEBenchValidator(
            data_points_dir=data_points_dir,
            timeout_per_instance=timeout,
            verbose=verbose,
        )
        
        # Run validation
        if files:
            # Validate specific files
            results = validator.validate_specific_files(list(files))
        else:
            # Validate all files in directory
            results = validator.validate_directory()
        
        # Display results
        if output_format == "json":
            _display_json_results(results)
        else:
            _display_text_results(results)
        
        # Exit with appropriate code
        if results["errors"] > 0:
            sys.exit(1)
        elif results["failed"] > 0:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _display_text_results(results: dict):
    """Display validation results in text format."""
    # Summary panel
    summary_text = f"""
[bold]Validation Summary[/bold]
• Total files: {results['total_files']}
• Validated: {results['validated']}
• [green]Successful: {results['successful']}[/green]
• [red]Failed: {results['failed']}[/red]
• [yellow]Errors: {results['errors']}[/yellow]
    """
    
    console.print(Panel(summary_text, title="SWE-bench Validator Results", border_style="blue"))
    
    # Detailed results table
    if results["results"]:
        table = Table(title="Detailed Results")
        table.add_column("Instance ID", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Execution Time", style="magenta")
        table.add_column("Patch Applied", style="blue")
        table.add_column("Tests Executed", style="blue")
        table.add_column("Error Message", style="red")
        
        for result in results["results"]:
            status = "[green]PASS[/green]" if result.success else "[red]FAIL[/red]"
            patch_status = "✓" if result.patch_applied else "✗"
            tests_status = "✓" if result.tests_executed else "✗"
            error_msg = result.error_message or ""
            
            table.add_row(
                result.instance_id,
                status,
                f"{result.execution_time:.2f}s",
                patch_status,
                tests_status,
                error_msg
            )
        
        console.print(table)
    
    # Error details
    if results["error_details"]:
        console.print("\n[bold red]Error Details:[/bold red]")
        for error in results["error_details"]:
            console.print(f"  • {error}")


def _display_json_results(results: dict):
    """Display validation results in JSON format."""
    import json
    
    # Convert results to JSON-serializable format
    json_results = {
        "summary": {
            "total_files": results["total_files"],
            "validated": results["validated"],
            "successful": results["successful"],
            "failed": results["failed"],
            "errors": results["errors"],
        },
        "results": [
            {
                "instance_id": r.instance_id,
                "success": r.success,
                "error_message": r.error_message,
                "execution_time": r.execution_time,
                "patch_applied": r.patch_applied,
                "tests_executed": r.tests_executed,
                "fail_to_pass_results": r.fail_to_pass_results,
                "pass_to_pass_results": r.pass_to_pass_results,
            }
            for r in results["results"]
        ],
        "error_details": results["error_details"],
    }
    
    console.print(json.dumps(json_results, indent=2))


if __name__ == "__main__":
    main()
