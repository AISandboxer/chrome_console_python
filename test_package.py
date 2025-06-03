#!/usr/bin/env python3
"""Quick test script to verify chrome-console-capture package works."""

import sys
import os

# Add the current directory to Python path for testing before installation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from chrome_console_capture import ConsoleCapture, ChromeNotFoundError
    print("✓ Package imported successfully")
except ImportError as e:
    print(f"✗ Failed to import package: {e}")
    sys.exit(1)

# Create a simple test page
test_html = """
<html>
<head><title>Test Page</title></head>
<body>
<h1>Chrome Console Capture Test</h1>
<script>
    console.log("Test successful! Console capture is working.");
    console.info("Info message");
    console.warn("Warning message");
    console.error("Error message");
    console.log("Test object:", {status: "success", timestamp: Date.now()});
</script>
</body>
</html>
"""

# Write test HTML to temporary file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
    f.write(test_html)
    temp_file = f.name

print(f"✓ Created test HTML file: {temp_file}")

try:
    # Test console capture
    print("\nStarting console capture test...")
    print("Chrome browser will open. Close it or press Ctrl+C to stop.\n")
    
    capture = ConsoleCapture(
        url=f"file://{temp_file}",
        output_file="test_output.log"
    )
    
    capture.start()
    print("✓ Console capture started successfully")
    
    # Let it run for a few seconds
    import time
    time.sleep(3)
    
    capture.stop()
    print("✓ Console capture stopped successfully")
    
    # Check if output file was created
    if os.path.exists("test_output.log"):
        print("✓ Output file created successfully")
        with open("test_output.log", 'r') as f:
            content = f.read()
            if "Test successful" in content:
                print("✓ Console messages captured correctly")
            else:
                print("✗ Console messages not found in output")
    else:
        print("✗ Output file not created")
    
except ChromeNotFoundError:
    print("✗ Chrome browser not found. Please install Chrome to run this test.")
except KeyboardInterrupt:
    print("\n✓ Test interrupted by user")
except Exception as e:
    print(f"✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)
    print("\n✓ Cleanup completed")

print("\nTest complete!") 