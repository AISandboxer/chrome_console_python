"""
Chrome Console Capture - A Python package to capture Chrome console output via DevTools Protocol.

This package provides an easy way to launch Chrome and capture console messages
that would normally appear in the Developer Tools Console.
"""

from .capture import ConsoleCapture
from .exceptions import ChromeConnectionError, ChromeNotFoundError

__version__ = "0.1.0"
__all__ = ["ConsoleCapture", "ChromeConnectionError", "ChromeNotFoundError"] 