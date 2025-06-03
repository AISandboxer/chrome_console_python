#!/usr/bin/env python3
"""Basic example of using chrome-console-capture package."""

from chrome_console_capture import ConsoleCapture


def main():
    # Create a test HTML page with various console outputs
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Console Capture Test</title>
    </head>
    <body>
        <h1>Chrome Console Capture Test Page</h1>
        <p>Check your terminal to see the captured console output!</p>
        
        <script>
            // Log various console messages
            console.log("Page loaded successfully!");
            console.info("This is an info message");
            console.warn("This is a warning message");
            console.error("This is an error message");
            console.debug("This is a debug message");
            
            // Log objects and arrays
            console.log("User object:", {
                name: "John Doe",
                email: "john@example.com",
                age: 30
            });
            
            console.log("Array of numbers:", [1, 2, 3, 4, 5]);
            
            // Test console.table
            console.table([
                {name: "Alice", age: 25},
                {name: "Bob", age: 30},
                {name: "Charlie", age: 35}
            ]);
            
            // Test console.group
            console.group("User Actions");
            console.log("User clicked button");
            console.log("Form submitted");
            console.groupEnd();
            
            // Test console.time
            console.time("Operation");
            setTimeout(() => {
                console.timeEnd("Operation");
            }, 1000);
            
            // Generate an error with stack trace
            function causeError() {
                throw new Error("Something went wrong!");
            }
            
            setTimeout(() => {
                try {
                    causeError();
                } catch (e) {
                    console.error("Caught error:", e.message);
                }
            }, 2000);
            
            // Test console.assert
            console.assert(1 === 1, "This should not appear");
            console.assert(1 === 2, "This assertion failed!");
            
            // Test console.count
            for (let i = 0; i < 3; i++) {
                console.count("Loop iteration");
            }
        </script>
    </body>
    </html>
    """
    
    # Save the test HTML to a temporary file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(test_html)
        temp_file = f.name
    
    try:
        # Create console capture instance
        print("Starting Chrome Console Capture...")
        print("Press Ctrl+C to stop capturing\n")
        
        capture = ConsoleCapture(
            url=f"file://{temp_file}",
            output_file="console_output.log"
        )
        
        # Start capturing
        capture.start()
        
        # Wait for user to close browser or press Ctrl+C
        capture.wait_for_close()
        
        print("\nConsole output has been saved to 'console_output.log'")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    main() 