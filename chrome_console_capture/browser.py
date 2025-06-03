"""Chrome browser management utilities."""

import os
import platform
import subprocess
import time
import tempfile
import shutil
import psutil
import requests
from typing import Optional, Dict, Any

from .exceptions import ChromeNotFoundError, ChromeLaunchError, ChromeConnectionError


def find_chrome_executable() -> str:
    """Find Chrome executable path based on the operating system."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Windows":
        paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
        ]
    else:  # Linux and others
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
    
    # Check if chrome is in PATH
    chrome_in_path = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if chrome_in_path:
        return chrome_in_path
    
    # Check predefined paths
    for path in paths:
        if os.path.exists(path):
            return path
    
    raise ChromeNotFoundError(
        "Chrome executable not found. Please install Chrome or specify the path manually."
    )


class ChromeBrowser:
    """Manages Chrome browser instance with DevTools enabled."""
    
    def __init__(self, chrome_path: Optional[str] = None, user_data_dir: Optional[str] = None):
        """
        Initialize Chrome browser manager.
        
        Args:
            chrome_path: Path to Chrome executable. If None, will auto-detect.
            user_data_dir: Chrome user data directory. If None, will use temporary directory.
        """
        self.chrome_path = chrome_path or find_chrome_executable()
        self.user_data_dir = user_data_dir
        self._temp_dir = None
        self.process = None
        self.devtools_url = None
        self.ws_url = None
        
    def launch(self, url: str, port: int = 9222, headless: bool = False, 
               window_size: Optional[tuple] = None, extra_args: Optional[list] = None) -> Dict[str, Any]:
        """
        Launch Chrome with remote debugging enabled.
        
        Args:
            url: URL to open in Chrome
            port: Remote debugging port (default: 9222)
            headless: Run Chrome in headless mode
            window_size: Window size as (width, height) tuple
            extra_args: Additional Chrome command line arguments
            
        Returns:
            Dictionary with connection details
        """
        # Create temporary user data directory if not provided
        if not self.user_data_dir:
            self._temp_dir = tempfile.mkdtemp(prefix="chrome_console_")
            self.user_data_dir = self._temp_dir
        
        # Build Chrome arguments
        args = [
            self.chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",  # Allow WebSocket connections from any origin
        ]
        
        if headless:
            args.append("--headless")
            args.append("--disable-gpu")
        
        if window_size:
            args.append(f"--window-size={window_size[0]},{window_size[1]}")
        
        if extra_args:
            args.extend(extra_args)
        
        # Add the URL as the last argument
        args.append(url)
        
        try:
            # Launch Chrome
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for Chrome to start and DevTools to be available
            self.devtools_url = f"http://localhost:{port}"
            self._wait_for_devtools(timeout=10)
            
            # Get WebSocket URL for the first tab
            self.ws_url = self._get_ws_url()
            
            return {
                "pid": self.process.pid,
                "devtools_url": self.devtools_url,
                "ws_url": self.ws_url,
                "user_data_dir": self.user_data_dir
            }
            
        except Exception as e:
            self.cleanup()
            raise ChromeLaunchError(f"Failed to launch Chrome: {str(e)}")
    
    def _wait_for_devtools(self, timeout: int = 10):
        """Wait for DevTools to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.devtools_url}/json/version", timeout=1)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        
        raise ChromeConnectionError(f"DevTools not available after {timeout} seconds")
    
    def _get_ws_url(self) -> str:
        """Get WebSocket URL for the first tab."""
        try:
            response = requests.get(f"{self.devtools_url}/json/list")
            response.raise_for_status()
            tabs = response.json()
            
            if not tabs:
                raise ChromeConnectionError("No tabs found in Chrome")
            
            # Find the first page (not extension or devtools)
            for tab in tabs:
                if tab.get("type") == "page":
                    return tab.get("webSocketDebuggerUrl")
            
            # Fallback to first tab if no page found
            return tabs[0].get("webSocketDebuggerUrl")
            
        except Exception as e:
            raise ChromeConnectionError(f"Failed to get WebSocket URL: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if Chrome process is still running."""
        if self.process is None:
            return False
        
        # Check if process is still alive
        return self.process.poll() is None
    
    def terminate(self):
        """Terminate Chrome process."""
        if self.process and self.is_running():
            try:
                # Try graceful termination first
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination fails
                self.process.kill()
                self.process.wait()
    
    def cleanup(self):
        """Clean up resources."""
        self.terminate()
        
        # Remove temporary directory if created
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
        
        self.process = None
        self.devtools_url = None
        self.ws_url = None 