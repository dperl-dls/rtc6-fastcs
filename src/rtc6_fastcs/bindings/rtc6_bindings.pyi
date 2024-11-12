"""
bindings for the scanlab rtc6 ethernet laser controller
"""

from __future__ import annotations

__all__ = [
    "CardInfo",
    "RtcConnectionError",
    "RtcError",
    "add",
    "check_connection",
    "close",
    "close_again",
    "connect",
    "get_card_info",
    "get_last_error",
    "ip_int_to_str",
    "ip_str_to_int",
    "throw_rtc_error",
]

class CardInfo:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    @property
    def firmware_version(self) -> int: ...
    @property
    def ip_address(self) -> str: ...
    @property
    def is_acquired(self) -> bool: ...
    @property
    def serial_number(self) -> int: ...

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

def close_again() -> None:
    """
    close the open connection, if any
    """

def connect(ip_string: str, program_file_path: str, correction_file_path: str) -> int:
    """
    connect to the eth-box at the given IP
    """

def get_card_info() -> CardInfo:
    """
    get info for the connected card; throws RtcConnectionError on failure
    """

def get_last_error() -> int:
    """
    get the last error for an ethernet command
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
