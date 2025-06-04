"""
Colored logging utility module.

This module provides colored console output for log messages.
"""

import logging
import os
import sys
from typing import Optional

# Try to import colorama for Windows color support
try:
    import colorama
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

class ColorCodes:
    """ANSI color codes for colored terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log messages based on their level."""

    COLORS = {
        'DEBUG': ColorCodes.BLUE,
        'INFO': ColorCodes.GREEN,
        'WARNING': ColorCodes.YELLOW,
        'ERROR': ColorCodes.RED,
        'CRITICAL': ColorCodes.BRIGHT_RED + ColorCodes.BOLD,
    }

    def format(self, record):
        """Format the log record with appropriate colors."""
        # Get the log level color
        level_color = self.COLORS.get(record.levelname, ColorCodes.RESET)

        # Format the log message
        formatted_msg = super().format(record)

        # Emphasis on level name - bold colored background
        if hasattr(record, 'levelname'):
            # Replace levelname in the formatted message with colored version
            level_display = record.levelname
            level_colored = f"{level_color}{level_display}{ColorCodes.RESET}"
            formatted_msg = formatted_msg.replace(level_display, level_colored)

        return formatted_msg


def enable_windows_ansi_support():
    """
    Enable ANSI color support in Windows console.

    On Windows, ANSI color codes are not natively supported in many consoles.
    This function enables support where possible, either through colorama
    or by enabling the VIRTUAL_TERMINAL_PROCESSING console mode.
    """
    if os.name != 'nt':
        return True

    # If colorama is available, it's already initialized
    if COLORAMA_AVAILABLE:
        return True

    # Try to enable ANSI support through Windows API as fallback
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32

        # Get the console mode
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))

        # Enable VIRTUAL_TERMINAL_PROCESSING
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
        success = kernel32.SetConsoleMode(handle, mode)

        return success != 0
    except Exception:
        return False


def is_color_supported() -> bool:
    """
    Check if the current terminal supports colors.

    Returns:
        True if colors are supported, False otherwise
    """
    # Enable Windows ANSI support if needed
    if os.name == 'nt':
        if enable_windows_ansi_support():
            return True

        # Fallback to environment variable checks
        return (
            'ANSICON' in os.environ
            or 'WT_SESSION' in os.environ
            or 'ConEmuANSI' in os.environ
            or os.environ.get('TERM') == 'xterm'
        )

    # Check if we're in a real terminal (not a pipe or file)
    # or if FORCE_COLOR environment variable is set
    return sys.stdout.isatty() or os.environ.get('FORCE_COLOR', '').lower() in ('1', 'true', 'yes')


def setup_colored_logger(
    logger_name: Optional[str] = None,
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    use_file_handler: bool = False,
    log_file: str = "zchat.log"
) -> logging.Logger:
    """
    Set up a logger with colored console output.

    Args:
        logger_name: Name of the logger (None for root logger)
        log_level: Logging level (e.g., logging.DEBUG, logging.INFO)
        log_format: Format string for log messages
        use_file_handler: Whether to also log to a file
        log_file: Path to the log file if use_file_handler is True

    Returns:
        The configured logger
    """
    # Get the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set up console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)

    if is_color_supported():
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Optionally add file handler
    if use_file_handler:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def setup_root_logger(
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: str = "zchat.log"
) -> None:
    """
    Configure the root logger with colored console output and file output.

    Args:
        log_level: Logging level (e.g., logging.DEBUG, logging.INFO)
        log_format: Format string for log messages
        log_file: Path to the log file
    """
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Set up console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)

    if is_color_supported():
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)

    console_handler.setFormatter(console_formatter)

    # # Configure the root logger
    # logging.basicConfig(
    #     level=log_level,
    #     handlers=[
    #         # file_handler,
    #         # console_handler
    #     ]
    # )
