# Chrome Console Capture

A Python package that captures console output from Chrome browser tabs using the Chrome DevTools Protocol. Perfect for debugging web applications, capturing JavaScript logs, and monitoring browser console output programmatically.

## Features

- 🚀 **Easy to use** - Simple API to launch Chrome and capture console output
- 📝 **Full console capture** - Captures all console methods (log, error, warn, info, debug, etc.)
- 🎨 **Formatted output** - Color-coded terminal output with timestamps
- 💾 **File logging** - Optionally save console output to a file
- 🔍 **Exception tracking** - Captures JavaScript runtime exceptions with stack traces
- 🎯 **Type filtering** - Filter to capture only specific console message types
- 🖥️ **Cross-platform** - Works on Windows, macOS, and Linux
- 🔄 **Real-time streaming** - See console messages as they happen

## Installation

```bash
pip install chrome-console-capture
```

Or install from source:

```bash
git clone https://github.com/yourusername/chrome-console-capture.git
cd chrome-console-capture
pip install -e .
```

## Quick Start

```python
from chrome_console_capture import ConsoleCapture

# Create a capture instance and start capturing
capture = ConsoleCapture(url="https://example.com")
capture.start()

# Wait for the browser to close or press Ctrl+C
capture.wait_for_close()
```

## Usage Examples

### Basic Usage

```python
from chrome_console_capture import ConsoleCapture

# Capture console output from a webpage
with ConsoleCapture(url="http://localhost:3000") as capture:
    capture.wait_for_close()
```

### Save Output to File

```python
from chrome_console_capture import ConsoleCapture

# Save console output to a file
capture = ConsoleCapture(
    url="https://example.com",
    output_file="console_output.log"
)
capture.start()
capture.wait_for_close()
```

### Filter Console Types

```python
from chrome_console_capture import ConsoleCapture

# Only capture errors and warnings
capture = ConsoleCapture(
    url="https://example.com",
    filter_types=["error", "warning"]
)
capture.start()
capture.wait_for_close()
```

### Headless Mode

```python
from chrome_console_capture import ConsoleCapture

# Run Chrome in headless mode (no GUI)
capture = ConsoleCapture(
    url="https://example.com",
    headless=True
)
capture.start()
capture.wait_for_close()
```

### Custom Chrome Path

```python
from chrome_console_capture import ConsoleCapture

# Use a specific Chrome installation
capture = ConsoleCapture(
    url="https://example.com",
    chrome_path="/path/to/chrome"
)
capture.start()
capture.wait_for_close()
```

### Raw JSON Output

```python
from chrome_console_capture import ConsoleCapture

# Get raw JSON output instead of formatted messages
capture = ConsoleCapture(
    url="https://example.com",
    format_output=False,
    output_file="console_raw.json"
)
capture.start()
capture.wait_for_close()
```

### Integration with Web Frameworks

#### Flask Example

```python
from flask import Flask
from chrome_console_capture import ConsoleCapture
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
        <script>
            console.log("Page loaded!");
            console.error("Example error");
            console.warn("Example warning");
            console.info("Example info");
        </script>
    </html>
    '''

def capture_console():
    capture = ConsoleCapture(url="http://localhost:5000")
    capture.start()
    capture.wait_for_close()

if __name__ == '__main__':
    # Start console capture in a separate thread
    capture_thread = threading.Thread(target=capture_console)
    capture_thread.start()
    
    # Run Flask app
    app.run(debug=True)
```

#### Django Example

```python
# In your Django management command or test
from django.core.management.base import BaseCommand
from chrome_console_capture import ConsoleCapture

class Command(BaseCommand):
    help = 'Capture browser console output during development'

    def handle(self, *args, **options):
        capture = ConsoleCapture(
            url="http://localhost:8000",
            output_file="django_console.log"
        )
        capture.start()
        self.stdout.write('Capturing console output... Press Ctrl+C to stop')
        capture.wait_for_close()
```

### Advanced Usage

#### Evaluate JavaScript

```python
from chrome_console_capture import ConsoleCapture

capture = ConsoleCapture(url="https://example.com")
capture.start()

# Evaluate JavaScript in the page context
result = capture.evaluate_expression("document.title")
print(f"Page title: {result}")

capture.stop()
```

#### Context Manager

```python
from chrome_console_capture import ConsoleCapture
import time

class ManagedCapture:
    def __init__(self, url, **kwargs):
        self.capture = ConsoleCapture(url, **kwargs)
    
    def __enter__(self):
        self.capture.start()
        return self.capture
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.capture.stop()

# Usage
with ManagedCapture("https://example.com") as capture:
    time.sleep(10)  # Capture for 10 seconds
```

## Output Format

### Formatted Output (Default)

```
[12:34:56.789] [LOG] Page loaded successfully
[12:34:56.790] [ERROR] Failed to fetch data: Network error
  Stack trace:
    at fetchData (https://example.com/app.js:45:12)
    at initialize (https://example.com/app.js:10:5)
[12:34:56.791] [WARN] Deprecated API usage detected
[12:34:56.792] [INFO] User logged in: user@example.com
```

### Raw JSON Output

```json
{
  "type": "error",
  "timestamp": "2024-01-01T12:34:56.790Z",
  "args": ["Failed to fetch data:", "Network error"],
  "stackTrace": {
    "callFrames": [
      {
        "functionName": "fetchData",
        "url": "https://example.com/app.js",
        "lineNumber": 45,
        "columnNumber": 12
      }
    ]
  }
}
```

## Console Types

The package captures all standard console methods:

- `log` - General output
- `error` - Error messages
- `warn` - Warning messages
- `info` - Informational messages
- `debug` - Debug messages
- `dir` - Directory listings
- `table` - Tabular data
- `trace` - Stack traces
- `assert` - Assertion failures
- `count` - Counter output
- `time`/`timeEnd` - Timer output
- `group`/`groupEnd` - Grouped messages

## API Reference

### ConsoleCapture

```python
ConsoleCapture(
    url: str,
    output_file: Optional[str] = None,
    chrome_path: Optional[str] = None,
    headless: bool = False,
    port: int = 9222,
    format_output: bool = True,
    filter_types: Optional[list] = None
)
```

#### Parameters

- **url** (str): The URL to open in Chrome
- **output_file** (str, optional): Path to save console output
- **chrome_path** (str, optional): Path to Chrome executable (auto-detected if not provided)
- **headless** (bool): Run Chrome in headless mode (default: False)
- **port** (int): Chrome remote debugging port (default: 9222)
- **format_output** (bool): Format messages for readability (default: True)
- **filter_types** (list, optional): List of console types to capture (default: all types)

#### Methods

- **start()**: Start capturing console output
- **stop()**: Stop capturing and clean up resources
- **wait_for_close()**: Wait for browser to close or user interrupt
- **evaluate_expression(expression: str)**: Evaluate JavaScript in the page context

## Error Handling

The package provides custom exceptions for better error handling:

```python
from chrome_console_capture import (
    ConsoleCapture,
    ChromeNotFoundError,
    ChromeConnectionError
)

try:
    capture = ConsoleCapture(url="https://example.com")
    capture.start()
    capture.wait_for_close()
except ChromeNotFoundError:
    print("Chrome browser not found. Please install Chrome.")
except ChromeConnectionError as e:
    print(f"Failed to connect to Chrome: {e}")
```

## Requirements

- Python 3.7+
- Chrome browser installed
- Dependencies:
  - websocket-client >= 1.3.0
  - requests >= 2.28.0
  - psutil >= 5.9.0

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/chrome-console-capture.git
cd chrome-console-capture

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black chrome_console_capture/

# Check code style
flake8 chrome_console_capture/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- Inspired by the need for better console debugging tools for web development

## Troubleshooting

### Chrome Not Found

If you get a "Chrome not found" error, you can:

1. Install Chrome from https://www.google.com/chrome/
2. Specify the Chrome path manually:
   ```python
   capture = ConsoleCapture(
       url="https://example.com",
       chrome_path="/path/to/chrome"
   )
   ```

### Port Already in Use

If port 9222 is already in use, specify a different port:

```python
capture = ConsoleCapture(
    url="https://example.com",
    port=9223
)
```

### Permission Errors

On macOS, you might need to allow Chrome to accept incoming network connections.
On Linux, ensure Chrome has necessary permissions.

## Support

- 📧 Email: your.email@example.com
- 🐛 Issues: https://github.com/yourusername/chrome-console-capture/issues
- 📖 Documentation: https://github.com/yourusername/chrome-console-capture/wiki 