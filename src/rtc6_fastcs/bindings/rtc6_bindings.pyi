"""
bindings for the scanlab rtc6 ethernet laser controller
"""

from __future__ import annotations
import typing

__all__ = [
    "CardInfo",
    "ListStatus",
    "RtcConnectionError",
    "RtcError",
    "RtcListError",
    "add",
    "check_connection",
    "close",
    "config_list_memory",
    "connect",
    "get_card_info",
    "get_config_list",
    "get_error",
    "get_error_string",
    "get_input_pointer",
    "get_io_status",
    "get_last_error",
    "get_list_space",
    "get_list_statuses",
    "get_rtc_mode",
    "get_temperature",
    "init_list_loading",
    "ip_int_to_str",
    "ip_str_to_int",
    "load_list",
    "set_laser_control",
    "set_laser_mode",
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

class ListStatus:
    """
    Members:

      LOAD1

      LOAD2

      READY1

      READY2

      BUSY1

      BUSY2

      USED1

      USED2
    """

    BUSY1: typing.ClassVar[ListStatus]  # value = <ListStatus.BUSY1: 4>
    BUSY2: typing.ClassVar[ListStatus]  # value = <ListStatus.BUSY2: 5>
    LOAD1: typing.ClassVar[ListStatus]  # value = <ListStatus.LOAD1: 0>
    LOAD2: typing.ClassVar[ListStatus]  # value = <ListStatus.LOAD2: 1>
    READY1: typing.ClassVar[ListStatus]  # value = <ListStatus.READY1: 2>
    READY2: typing.ClassVar[ListStatus]  # value = <ListStatus.READY2: 3>
    USED1: typing.ClassVar[ListStatus]  # value = <ListStatus.USED1: 6>
    USED2: typing.ClassVar[ListStatus]  # value = <ListStatus.USED2: 7>
    __members__: typing.ClassVar[
        dict[str, ListStatus]
    ]  # value = {'LOAD1': <ListStatus.LOAD1: 0>, 'LOAD2': <ListStatus.LOAD2: 1>, 'READY1': <ListStatus.READY1: 2>, 'READY2': <ListStatus.READY2: 3>, 'BUSY1': <ListStatus.BUSY1: 4>, 'BUSY2': <ListStatus.BUSY2: 5>, 'USED1': <ListStatus.USED1: 6>, 'USED2': <ListStatus.USED2: 7>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class RtcConnectionError(Exception):
    pass

class RtcError(Exception):
    pass

class RtcListError(Exception):
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

def config_list_memory(list_1_mem: int, list_2_mem: int) -> None:
    """
    set the memory for each position list, see p330
    """

def connect(ip_string: str, program_file_path: str, correction_file_path: str) -> int:
    """
    connect to the eth-box at the given IP
    """

def get_card_info() -> CardInfo:
    """
    get info for the connected card; throws RtcConnectionError on failure
    """

def get_config_list() -> None:
    """
    ---
    """

def get_error() -> int:
    """
    ---
    """

def get_error_string() -> str:
    """
    get human-readable error info
    """

def get_input_pointer() -> int:
    """
    get the pointer of list input
    """

def get_io_status() -> int:
    """
    ---
    """

def get_last_error() -> int:
    """
    get the last error for an ethernet command
    """

def get_list_space() -> int:
    """
    ---
    """

def get_list_statuses() -> list:
    """
    get the statuses of the command lists
    """

def get_rtc_mode() -> int:
    """
    ---
    """

def get_temperature() -> float:
    """
    ---
    """

def init_list_loading(arg0: int) -> None:
    """
    initialise the given list (1 or 2)
    """

def ip_int_to_str(ip_int: int) -> str:
    """
    convert IP address from int to string
    """

def ip_str_to_int(ip_string: str) -> int:
    """
    convert IP address from string to int
    """

def load_list(list_no: int, position: int) -> int:
    """
    set the pointer to load at position of list_no, see p330
    """

def set_laser_control(settings: int) -> None:
    """
    set the control settings of the laser, see p641
    """

def set_laser_mode(mode: int) -> None:
    """
    set the mode of the laser, see p645
    """

def throw_rtc_error(error_text: str) -> int:
    """
    throw an exception with the given text
    """
