"""Main console capture functionality using Chrome DevTools Protocol."""

import json
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Callable, Dict, Any, TextIO
from pathlib import Path

import websocket

from .browser import ChromeBrowser
from .exceptions import ChromeConnectionError


class ConsoleCapture:
    """Captures console output from Chrome using DevTools Protocol."""
    
    # Console API types as defined in Chrome DevTools Protocol
    CONSOLE_TYPES = {
        "log": "LOG",
        "debug": "DEBUG",
        "info": "INFO",
        "error": "ERROR",
        "warning": "WARN",
        "dir": "DIR",
        "dirxml": "DIRXML",
        "table": "TABLE",
        "trace": "TRACE",
        "clear": "CLEAR",
        "startGroup": "GROUP",
        "startGroupCollapsed": "GROUP_COLLAPSED",
        "endGroup": "GROUP_END",
        "assert": "ASSERT",
        "profile": "PROFILE",
        "profileEnd": "PROFILE_END",
        "count": "COUNT",
        "timeEnd": "TIME_END"
    }
    
    def __init__(self, 
                 url: str,
                 output_file: Optional[str] = None,
                 chrome_path: Optional[str] = None,
                 headless: bool = False,
                 port: int = 9222,
                 format_output: bool = True,
                 filter_types: Optional[list] = None):
        """
        Initialize console capture.
        
        Args:
            url: URL to open in Chrome
            output_file: Optional file path to write console output
            chrome_path: Path to Chrome executable (auto-detected if None)
            headless: Run Chrome in headless mode
            port: Chrome remote debugging port
            format_output: Format console messages for better readability
            filter_types: List of console types to capture (None = all types)
        """
        self.url = url
        self.output_file = output_file
        self.chrome_path = chrome_path
        self.headless = headless
        self.port = port
        self.format_output = format_output
        self.filter_types = filter_types or list(self.CONSOLE_TYPES.keys())
        
        self.browser = None
        self.ws = None
        self.running = False
        self.message_id = 1
        self._output_file_handle: Optional[TextIO] = None
        self._callbacks: Dict[str, Callable] = {}
        
    def start(self):
        """Start capturing console output."""
        try:
            # Launch Chrome
            self.browser = ChromeBrowser(self.chrome_path)
            launch_info = self.browser.launch(
                url=self.url,
                port=self.port,
                headless=self.headless
            )
            
            # Open output file if specified
            if self.output_file:
                self._output_file_handle = open(self.output_file, 'w', encoding='utf-8')
                self._write_output(f"# Console output for: {self.url}")
                self._write_output(f"# Started at: {datetime.now().isoformat()}")
                self._write_output("-" * 80)
            
            # Connect to Chrome via WebSocket
            self._connect_websocket(launch_info['ws_url'])
            
            # Enable console API
            self._enable_console()
            
            # Start message handling
            self.running = True
            self._start_message_loop()
            
        except Exception as e:
            self.stop()
            raise
    
    def stop(self):
        """Stop capturing and clean up resources."""
        self.running = False
        
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        
        if self._output_file_handle:
            self._write_output("-" * 80)
            self._write_output(f"# Ended at: {datetime.now().isoformat()}")
            self._output_file_handle.close()
        
        if self.browser:
            self.browser.cleanup()
    
    def _connect_websocket(self, ws_url: str):
        """Connect to Chrome via WebSocket."""
        try:
            self.ws = websocket.create_connection(ws_url, timeout=10)
        except Exception as e:
            raise ChromeConnectionError(f"Failed to connect to Chrome DevTools: {str(e)}")
    
    def _send_command(self, method: str, params: Optional[Dict] = None) -> int:
        """Send a command to Chrome DevTools."""
        command = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        self.ws.send(json.dumps(command))
        message_id = self.message_id
        self.message_id += 1
        
        return message_id
    
    def _enable_console(self):
        """Enable Console API in Chrome DevTools."""
        # Enable Runtime domain to receive console messages
        self._send_command("Runtime.enable")
        
        # Enable Console domain
        self._send_command("Console.enable")
        
        # Wait a bit for the domains to be enabled
        time.sleep(0.5)
    
    def _start_message_loop(self):
        """Start the WebSocket message handling loop."""
        def message_handler():
            while self.running:
                try:
                    message = self.ws.recv()
                    if message:
                        self._handle_message(json.loads(message))
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error receiving message: {str(e)}", file=sys.stderr)
                    break
        
        # Start message handler in a separate thread
        handler_thread = threading.Thread(target=message_handler, daemon=True)
        handler_thread.start()
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle messages from Chrome DevTools."""
        method = message.get("method")
        
        if method == "Runtime.consoleAPICalled":
            self._handle_console_message(message.get("params", {}))
        elif method == "Runtime.exceptionThrown":
            self._handle_exception(message.get("params", {}))
        
        # Handle callbacks for command responses
        message_id = message.get("id")
        if message_id and message_id in self._callbacks:
            callback = self._callbacks.pop(message_id)
            callback(message)
    
    def _handle_console_message(self, params: Dict[str, Any]):
        """Handle console API messages."""
        console_type = params.get("type", "log")
        
        # Filter by console type if specified
        if console_type not in self.filter_types:
            return
        
        # Extract message details
        timestamp = datetime.fromtimestamp(params.get("timestamp", 0) / 1000)
        args = params.get("args", [])
        stack_trace = params.get("stackTrace")
        
        # Format the message
        if self.format_output:
            output = self._format_console_message(
                console_type, timestamp, args, stack_trace
            )
        else:
            # Raw format
            output = json.dumps({
                "type": console_type,
                "timestamp": timestamp.isoformat(),
                "args": [self._serialize_runtime_object(arg) for arg in args],
                "stackTrace": stack_trace
            })
        
        self._write_output(output)
    
    def _handle_exception(self, params: Dict[str, Any]):
        """Handle runtime exceptions."""
        exception_details = params.get("exceptionDetails", {})
        timestamp = datetime.fromtimestamp(params.get("timestamp", 0) / 1000)
        
        # Format exception message
        if self.format_output:
            output = self._format_exception(timestamp, exception_details)
        else:
            output = json.dumps({
                "type": "exception",
                "timestamp": timestamp.isoformat(),
                "details": exception_details
            })
        
        self._write_output(output)
    
    def _format_console_message(self, console_type: str, timestamp: datetime, 
                               args: list, stack_trace: Optional[Dict]) -> str:
        """Format console message for output."""
        # Type label with color codes for terminal
        type_label = self.CONSOLE_TYPES.get(console_type, console_type.upper())
        
        # Color codes for different message types
        colors = {
            "error": "\033[91m",      # Red
            "warning": "\033[93m",    # Yellow
            "info": "\033[94m",       # Blue
            "debug": "\033[90m",      # Gray
            "log": "\033[0m",         # Default
        }
        
        color = colors.get(console_type, "\033[0m")
        reset = "\033[0m"
        
        # Format timestamp
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        # Format arguments
        formatted_args = []
        for arg in args:
            formatted_args.append(self._serialize_runtime_object(arg))
        
        message = " ".join(str(arg) for arg in formatted_args)
        
        # Build output
        output_parts = [
            f"{color}[{time_str}] [{type_label}]{reset}",
            message
        ]
        
        # Add stack trace if available
        if stack_trace and console_type in ["error", "warning", "trace"]:
            frames = stack_trace.get("callFrames", [])
            if frames:
                output_parts.append("\n  Stack trace:")
                for frame in frames[:5]:  # Limit to 5 frames
                    func_name = frame.get("functionName", "<anonymous>")
                    url = frame.get("url", "")
                    line = frame.get("lineNumber", 0)
                    col = frame.get("columnNumber", 0)
                    output_parts.append(f"    at {func_name} ({url}:{line}:{col})")
        
        return " ".join(output_parts)
    
    def _format_exception(self, timestamp: datetime, exception_details: Dict) -> str:
        """Format exception for output."""
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        text = exception_details.get("text", "Unknown exception")
        exception_obj = exception_details.get("exception", {})
        description = exception_obj.get("description", text)
        
        output = f"\033[91m[{time_str}] [EXCEPTION]\033[0m {description}"
        
        # Add stack trace if available
        stack_trace = exception_details.get("stackTrace")
        if stack_trace:
            frames = stack_trace.get("callFrames", [])
            if frames:
                output += "\n  Stack trace:"
                for frame in frames[:5]:
                    func_name = frame.get("functionName", "<anonymous>")
                    url = frame.get("url", "")
                    line = frame.get("lineNumber", 0)
                    col = frame.get("columnNumber", 0)
                    output += f"\n    at {func_name} ({url}:{line}:{col})"
        
        return output
    
    def _serialize_runtime_object(self, obj: Dict) -> Any:
        """Serialize Chrome Runtime.RemoteObject to Python object."""
        obj_type = obj.get("type")
        
        if obj_type == "undefined":
            return "undefined"
        elif obj_type == "object":
            if obj.get("subtype") == "null":
                return "null"
            else:
                # Try to get preview or description
                preview = obj.get("preview")
                if preview:
                    return self._serialize_object_preview(preview)
                return obj.get("description", "[object]")
        elif obj_type in ["string", "number", "boolean"]:
            return obj.get("value")
        elif obj_type == "function":
            return obj.get("description", "[function]")
        elif obj_type == "symbol":
            return obj.get("description", "[symbol]")
        else:
            return obj.get("value", obj.get("description", "[unknown]"))
    
    def _serialize_object_preview(self, preview: Dict) -> str:
        """Serialize object preview."""
        obj_type = preview.get("type")
        subtype = preview.get("subtype")
        
        if subtype == "array":
            # Format array preview
            properties = preview.get("properties", [])
            items = []
            for prop in properties:
                if prop.get("name", "").isdigit():  # Array indices
                    items.append(self._serialize_property_value(prop))
            
            overflow = preview.get("overflow", False)
            result = f"[{', '.join(items)}"
            if overflow:
                result += ", ..."
            result += "]"
            return result
        
        elif obj_type == "object":
            # Format object preview
            properties = preview.get("properties", [])
            items = []
            for prop in properties:
                name = prop.get("name")
                value = self._serialize_property_value(prop)
                items.append(f"{name}: {value}")
            
            overflow = preview.get("overflow", False)
            result = f"{{{', '.join(items)}"
            if overflow:
                result += ", ..."
            result += "}"
            return result
        
        else:
            return preview.get("description", "[object]")
    
    def _serialize_property_value(self, prop: Dict) -> str:
        """Serialize property value from preview."""
        prop_type = prop.get("type")
        
        if prop_type == "undefined":
            return "undefined"
        elif prop_type == "object":
            if prop.get("subtype") == "null":
                return "null"
            return prop.get("value", "[object]")
        elif prop_type in ["string", "number", "boolean"]:
            value = prop.get("value")
            if prop_type == "string":
                return f'"{value}"'
            return str(value)
        else:
            return prop.get("value", "[unknown]")
    
    def _write_output(self, message: str):
        """Write output to terminal and/or file."""
        # Always write to terminal
        print(message)
        
        # Write to file if specified
        if self._output_file_handle:
            self._output_file_handle.write(message + "\n")
            self._output_file_handle.flush()
    
    def wait_for_close(self):
        """Wait for the browser to close or user interrupt."""
        try:
            while self.running and self.browser and self.browser.is_running():
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopping console capture...")
        finally:
            self.stop()
    
    def add_callback(self, message_id: int, callback: Callable):
        """Add a callback for a specific message ID."""
        self._callbacks[message_id] = callback
    
    def evaluate_expression(self, expression: str) -> Any:
        """
        Evaluate JavaScript expression in the page context.
        
        Args:
            expression: JavaScript expression to evaluate
            
        Returns:
            Result of the expression
        """
        result = {"done": False, "value": None}
        
        def handle_response(response):
            if "result" in response:
                result["value"] = self._serialize_runtime_object(
                    response["result"].get("result", {})
                )
            result["done"] = True
        
        message_id = self._send_command(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True
            }
        )
        
        self.add_callback(message_id, handle_response)
        
        # Wait for response
        timeout = 5
        start_time = time.time()
        while not result["done"] and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        return result["value"] 