"""
bindings for the scanlab rtc6 ethernet laser controller
"""

from __future__ import annotations

__all__ = [
    "RtcConnectionError",
    "RtcError",
    "add",
    "check_connection",
    "close",
    "connect",
    "ip_int_to_str",
    "ip_str_to_int",
    "throw_rtc_error",
]

class RtcConnectionError(Exception):
    pass

class RtcError(Exception):
    pass

def add(i: int, j: int) -> int:
    """
    A function that adds two numbers
    """

def check_connection() -> None:
    """
    check the active connection to the eth box: throws RtcConnectionError on failure, otherwise does nothing.
    """

def close() -> None:
    """
    close the open connection, if any
    """

def connect(ip_string: str, program_file_path: str, correction_file_path: str) -> None:
    """
    connect to the eth-box at the given IP
    """

def ip_int_to_str(ip_int: int) -> str:
    """
    convert IP address from int to string
    """

def ip_str_to_int(ip_string: str) -> int:
    """
    convert IP address from string to int
    """

def throw_rtc_error(error_text: str) -> int:
    """
    throw an exception with the given text
    """
