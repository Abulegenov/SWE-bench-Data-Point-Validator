# SWE-bench Docker Architecture

## Overview

SWE-bench uses a sophisticated 3-layer Docker architecture to ensure reproducible and isolated evaluation of software engineering tasks. This system allows SWE-bench to test AI-generated patches against real-world codebases in a controlled environment that closely mimics the original development context.

## The 3-Layer Docker System

### Layer 1: Base Image
The foundation layer provides a clean, standardized environment for all evaluations.

**Purpose**: Establishes the base operating system and core dependencies that all evaluations will share.

**Contents**:
- Ubuntu Linux base image
- Python runtime environment
- Basic system tools and utilities
- Common development dependencies (git, curl, wget, etc.)

**Why it matters**: This layer ensures consistency across all evaluations, eliminating "works on my machine" issues that plague software development.

### Layer 2: Environment Image
The middle layer sets up the specific environment needed for a particular repository or project.

**Purpose**: Installs project-specific dependencies, sets up the development environment, and prepares the codebase for testing.

**Contents**:
- Repository-specific dependencies (from requirements.txt, setup.py, etc.)
- Database setup and configuration
- Environment variables and configuration files
- Test framework installation and configuration
- Any additional tools needed for the specific project

**When it's built**: This image is built when SWE-bench first encounters a new repository or when dependencies change significantly.

**Example**: For a Django project, this layer would install Django, database drivers, and other web framework dependencies.

### Layer 3: Instance Image
The top layer contains the specific codebase state and test cases for a particular SWE-bench instance.

**Purpose**: Captures the exact state of the codebase at the time of the issue, including the failing tests and the environment needed to reproduce the problem.

**Contents**:
- The exact codebase at the specified commit
- The specific test cases that need to be run
- Any additional setup required for that particular issue
- The patch that will be applied during evaluation

**When it's built**: This image is built for each individual SWE-bench instance, ensuring perfect isolation between different evaluation tasks.

## Image Building Process

### When Images Are Built

**Base Image**: Built once and reused across all evaluations. Updated only when core system dependencies change.

**Environment Image**: Built when:
- A new repository is encountered for the first time
- Dependencies in the repository change significantly
- The base image is updated
- Manual refresh is requested

**Instance Image**: Built for every individual SWE-bench instance, ensuring each evaluation runs in a completely isolated environment.

### How Images Are Built

1. **Dependency Resolution**: SWE-bench analyzes the repository's dependency files (requirements.txt, setup.py, pyproject.toml, etc.)

2. **Dockerfile Generation**: Creates optimized Dockerfiles for each layer, using multi-stage builds to minimize image size

3. **Layer Caching**: Leverages Docker's layer caching to speed up rebuilds when only minor changes occur

4. **Dependency Installation**: Installs dependencies in the correct order, handling conflicts and version constraints

5. **Environment Setup**: Configures the environment variables, database connections, and other project-specific settings

## Test Execution Flow

### 1. Container Initialization
When an evaluation begins, SWE-bench:
- Pulls or builds the required instance image
- Starts a fresh container from that image
- Sets up the evaluation environment
- Prepares the codebase for testing

### 2. Patch Application Process
The core of SWE-bench's evaluation involves applying the AI-generated patch:

```bash
# 1. Checkout the base commit
git checkout <base_commit>

# 2. Apply the patch
git apply <patch_file>

# 3. Verify patch application
git status
git diff --cached
```

**Error Handling**: If patch application fails, the evaluation is marked as failed with detailed error messages about what went wrong.

### 3. Test Command Execution
After successful patch application, SWE-bench runs the specified tests:

**FAIL_TO_PASS Tests**: These are tests that were failing before the patch and should pass after applying the fix.

**PASS_TO_PASS Tests**: These are tests that were already passing and should continue to pass after the patch.

**Execution Process**:
```bash
# Run FAIL_TO_PASS tests
pytest <fail_to_pass_tests> --tb=short

# Run PASS_TO_PASS tests  
pytest <pass_to_pass_tests> --tb=short
```

### 4. Timeout Handling
SWE-bench implements sophisticated timeout management:

- **Per-test timeouts**: Individual tests are limited to prevent infinite loops
- **Overall evaluation timeout**: Entire evaluation is capped to prevent resource exhaustion
- **Graceful degradation**: When timeouts occur, partial results are still captured and reported

### 5. Output Parsing and Result Extraction
The system carefully parses test outputs to determine success or failure:

- **Exit codes**: Captures and interprets pytest exit codes
- **Test output parsing**: Extracts individual test results from pytest output
- **Error message capture**: Captures detailed error messages for debugging
- **Performance metrics**: Records execution time and resource usage

## Integration Points with Validation System

### How the Validator Integrates

The SWE-bench validator leverages this Docker infrastructure by:

1. **Using the Official Harness**: The validator calls `swebench.harness.run_evaluation()` which handles all Docker operations internally

2. **Data Point Conversion**: Converts SWE-bench data points into the prediction format expected by the evaluation harness

3. **Result Interpretation**: Processes the evaluation results to determine if patches are valid

### Key Integration Points

**Docker Image Management**: The validator doesn't need to manage Docker images directly - the SWE-bench harness handles this automatically.

**Environment Isolation**: Each validation runs in a completely isolated container, preventing interference between different evaluations.

**Resource Management**: The harness manages CPU, memory, and disk usage, ensuring fair resource allocation.

## When and Where Data Point Requirements Are Installed

### Installation Timeline

**Pre-evaluation**: All dependencies are installed during the Environment Image build phase, before any evaluation begins.

**Per-instance**: Additional instance-specific requirements are installed when building the Instance Image.

**Runtime**: No additional installations occur during evaluation - everything needed is already in the container.

### Installation Locations

**System Dependencies**: Installed in the Base Image layer for maximum reusability.

**Project Dependencies**: Installed in the Environment Image layer, specific to each repository.

**Test Dependencies**: Installed as part of the Environment Image build process.

**Instance-specific Requirements**: Any additional requirements for specific instances are installed in the Instance Image layer.

## Concrete Execution Examples

### Example 1: Django Issue Evaluation

```bash
# 1. Container starts with Django environment pre-installed
# 2. Codebase is checked out at the specific commit
# 3. AI patch is applied
# 4. Tests are run:
pytest tests/test_views.py::TestUserView::test_user_creation
pytest tests/test_models.py::TestUserModel::test_user_validation
# 5. Results are captured and returned
```

### Example 2: Astropy Issue Evaluation

```bash
# 1. Container starts with scientific Python stack
# 2. Astropy codebase is prepared
# 3. Patch handling NoConvergence exception is applied
# 4. Specific WCS tests are executed:
pytest astropy/wcs/wcsapi/tests/test_fitswcs.py::test_non_convergence_warning
# 5. Test results determine if the patch properly fixes the issue
```

## Benefits of This Architecture

### Reproducibility
Every evaluation runs in exactly the same environment, ensuring consistent results across different machines and time periods.

### Isolation
Each evaluation is completely isolated, preventing interference between different patches or test cases.

### Scalability
The layered approach allows for efficient resource usage and parallel evaluation of multiple instances.

### Maintainability
The modular design makes it easy to update dependencies or add support for new types of projects.

## Conclusion

SWE-bench's Docker architecture provides a robust, scalable foundation for evaluating AI-generated code patches. The 3-layer system ensures reproducibility while the sophisticated test execution flow provides detailed insights into patch effectiveness. This architecture is what makes SWE-bench a reliable benchmark for measuring AI coding capabilities in real-world scenarios.

For validator implementers, understanding this architecture is crucial for properly integrating with the SWE-bench evaluation harness and ensuring that validation results are accurate and meaningful.
