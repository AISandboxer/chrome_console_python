#!/usr/bin/env python3
"""Example of integrating chrome-console-capture with a Flask application."""

from flask import Flask, render_template_string
from chrome_console_capture import ConsoleCapture
import threading
import time
import os


app = Flask(__name__)


# HTML template with JavaScript that generates console output
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Console Capture Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        button {
            margin: 10px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        #api-response {
            margin-top: 20px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Flask + Chrome Console Capture Demo</h1>
    <p>This page demonstrates capturing console output from a Flask application.</p>
    
    <h2>Test Console Output</h2>
    <button onclick="testLogs()">Generate Logs</button>
    <button onclick="testError()">Generate Error</button>
    <button onclick="testAPI()">Test API Call</button>
    <button onclick="testPerformance()">Test Performance</button>
    
    <div id="api-response"></div>
    
    <script>
        // Log page load
        console.log("Flask app page loaded at", new Date().toISOString());
        console.info("Application ready");
        
        function testLogs() {
            console.log("Test log message");
            console.info("Test info message");
            console.warn("Test warning message");
            console.debug("Test debug message");
            
            // Log object
            console.log("User data:", {
                id: 123,
                name: "Test User",
                roles: ["admin", "user"]
            });
        }
        
        function testError() {
            console.error("Test error message");
            
            // Cause an actual error
            try {
                nonExistentFunction();
            } catch (e) {
                console.error("Caught exception:", e.message);
                console.error(e);
            }
        }
        
        async function testAPI() {
            console.log("Making API request...");
            console.time("API Request");
            
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                console.log("API Response:", data);
                document.getElementById('api-response').innerHTML = 
                    '<strong>API Response:</strong> ' + JSON.stringify(data, null, 2);
                
            } catch (error) {
                console.error("API request failed:", error);
            } finally {
                console.timeEnd("API Request");
            }
        }
        
        function testPerformance() {
            console.group("Performance Test");
            
            // Test with timing
            console.time("Calculation");
            
            let sum = 0;
            for (let i = 0; i < 1000000; i++) {
                sum += i;
            }
            
            console.timeEnd("Calculation");
            console.log("Sum:", sum);
            
            // Memory info (if available)
            if (performance.memory) {
                console.table({
                    "Used JS Heap": performance.memory.usedJSHeapSize,
                    "Total JS Heap": performance.memory.totalJSHeapSize,
                    "Limit": performance.memory.jsHeapSizeLimit
                });
            }
            
            console.groupEnd();
        }
        
        // Monitor for errors
        window.addEventListener('error', (event) => {
            console.error('Global error caught:', event.error);
        });
        
        // Monitor for unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page route."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/data')
def api_data():
    """Sample API endpoint."""
    import json
    return json.dumps({
        'status': 'success',
        'timestamp': time.time(),
        'data': {
            'items': [1, 2, 3, 4, 5],
            'message': 'Data retrieved successfully'
        }
    })


def run_console_capture(port=5000):
    """Run Chrome console capture in a separate thread."""
    # Wait a bit for Flask to start
    time.sleep(2)
    
    print("\n" + "="*50)
    print("Starting Chrome Console Capture...")
    print("Console output will be displayed below")
    print("="*50 + "\n")
    
    try:
        capture = ConsoleCapture(
            url=f"http://localhost:{port}",
            output_file="flask_console.log"
        )
        capture.start()
        capture.wait_for_close()
    except Exception as e:
        print(f"Console capture error: {e}")


def main():
    """Run Flask app with console capture."""
    port = int(os.environ.get('PORT', 5000))
    
    # Start console capture in a separate thread
    capture_thread = threading.Thread(
        target=run_console_capture,
        args=(port,),
        daemon=True
    )
    capture_thread.start()
    
    # Run Flask app
    print(f"Starting Flask app on http://localhost:{port}")
    print("The browser will open automatically to capture console output")
    print("Press Ctrl+C to stop both Flask and console capture\n")
    
    try:
        app.run(debug=True, port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == '__main__':
    main() 