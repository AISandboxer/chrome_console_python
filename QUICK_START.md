# Chrome Console Capture - Quick Start Guide

## What is this?

A Python package that captures console output from Chrome browser tabs using the Chrome DevTools Protocol. It streams console messages (log, error, warn, etc.) to your terminal and optionally to a file.

## Installation

### From PyPI (when published)
```bash
pip install chrome-console-capture
```

### From Source (current method)
```bash
# Clone or download this repository
cd chrome_console_python

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Basic Usage

### 1. Simple Console Capture

```python
from chrome_console_capture import ConsoleCapture

# Capture console output from any URL
capture = ConsoleCapture(url="https://example.com")
capture.start()
capture.wait_for_close()  # Wait until browser is closed
```

### 2. Save to File

```python
capture = ConsoleCapture(
    url="https://example.com",
    output_file="console.log"
)
capture.start()
capture.wait_for_close()
```

### 3. Integration with Flask/Django

```python
# In your web app development
from chrome_console_capture import ConsoleCapture
import threading

def capture_console():
    capture = ConsoleCapture(url="http://localhost:8000")
    capture.start()
    capture.wait_for_close()

# Start in background thread
thread = threading.Thread(target=capture_console, daemon=True)
thread.start()

# Run your web app
# app.run()  # Flask
# manage.py runserver  # Django
```

## Test the Package

Run the included test script:

```bash
python test_package.py
```

This will:
1. Launch Chrome with a test page
2. Capture console output
3. Save it to `test_output.log`
4. Verify everything works

## Examples

Check the `examples/` directory:
- `basic_example.py` - Comprehensive console testing
- `flask_integration.py` - Flask app integration

Run examples:
```bash
python examples/basic_example.py
python examples/flask_integration.py
```

## Features

- ✅ Captures all console types (log, error, warn, info, debug, etc.)
- ✅ Real-time streaming to terminal
- ✅ Optional file logging
- ✅ Formatted output with colors and timestamps
- ✅ Stack traces for errors
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Headless mode support
- ✅ Easy integration with web frameworks

## Requirements

- Python 3.7+
- Chrome browser installed
- Dependencies (auto-installed):
  - websocket-client
  - requests
  - psutil

## Troubleshooting

**Chrome not found?**
```python
# Specify Chrome path manually
capture = ConsoleCapture(
    url="https://example.com",
    chrome_path="/path/to/chrome"
)
```

**Port conflict?**
```python
# Use different port
capture = ConsoleCapture(
    url="https://example.com",
    port=9223  # Default is 9222
)
```

## Next Steps

1. Install the package
2. Run `test_package.py` to verify it works
3. Try the examples
4. Integrate into your project

For full documentation, see `README.md`. 