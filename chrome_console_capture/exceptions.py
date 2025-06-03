"""Custom exceptions for chrome-console-capture package."""


class ChromeConsoleError(Exception):
    """Base exception for chrome-console-capture."""
    pass


class ChromeNotFoundError(ChromeConsoleError):
    """Raised when Chrome executable cannot be found."""
    pass


class ChromeConnectionError(ChromeConsoleError):
    """Raised when connection to Chrome DevTools fails."""
    pass


class ChromeLaunchError(ChromeConsoleError):
    """Raised when Chrome fails to launch."""
    pass 