# Virtual Environment Setup Guide

This guide shows how to set up and use a virtual environment for testing and developing with the chrome-console-capture package.

## Why Use a Virtual Environment?

Virtual environments provide:
- **Isolation**: Dependencies won't conflict with other Python projects
- **Clean Testing**: Ensures the package works with only its declared dependencies
- **Easy Cleanup**: Simply delete the venv folder to remove everything

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to the project directory
cd chrome_console_python

# Create virtual environment
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You'll see `(venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
# Install package dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Or install normally
pip install .
```

### 4. Run Tests

```bash
# Test basic functionality
python test_package.py

# Run examples
python examples/basic_example.py
python examples/flask_integration.py
```

## Development Workflow

### Installing Development Dependencies

```bash
# Install dev dependencies
pip install -e ".[dev]"

# This includes:
# - pytest for testing
# - black for code formatting
# - flake8 for linting
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chrome_console_capture

# Format code
black chrome_console_capture/

# Check code style
flake8 chrome_console_capture/
```

## Common Commands

```bash
# Check installed packages
pip list

# Update pip
pip install --upgrade pip

# Generate requirements file
pip freeze > requirements-dev.txt

# Deactivate virtual environment
deactivate
```

## Troubleshooting

### Virtual Environment Not Activating

Make sure you're in the correct directory and the venv was created successfully:
```bash
ls -la venv/  # Should show bin/, lib/, etc.
```

### Import Errors

Ensure the package is installed in the virtual environment:
```bash
# With venv activated
pip show chrome-console-capture
```

### Clean Reinstall

```bash
# Deactivate if active
deactivate

# Remove virtual environment
rm -rf venv/

# Start fresh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Testing in Different Python Versions

```bash
# Create venvs for different Python versions
python3.7 -m venv venv37
python3.8 -m venv venv38
python3.9 -m venv venv39
python3.10 -m venv venv310
python3.11 -m venv venv311

# Activate and test each
source venv37/bin/activate
pip install -r requirements.txt
python test_package.py
deactivate
```

## GitHub Actions Integration

For CI/CD, you can use virtual environments in GitHub Actions:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e .
    - name: Test
      run: |
        python test_package.py
```

## Best Practices

1. **Always activate the virtual environment** before working on the project
2. **Keep requirements.txt updated** when adding new dependencies
3. **Use separate virtual environments** for different projects
4. **Add venv/ to .gitignore** (already done in this project)
5. **Document Python version requirements** in README.md

## Quick Reference

```bash
# Full setup from scratch
git clone <repo-url>
cd chrome_console_python
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
python test_package.py
``` 