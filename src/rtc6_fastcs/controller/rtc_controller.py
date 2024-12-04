import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from fastcs.attributes import AttrR, AttrW, AttrRW, Sender
from fastcs.controller import Controller, SubController
from fastcs.datatypes import Bool, Float, Int, String
from fastcs.wrappers import command

from py import process
from rtc6_fastcs.controller.rtc_connection import RtcConnection


class ConnectedSubController(SubController):
    def __init__(self, conn: RtcConnection) -> None:
        super().__init__()
        self._conn = conn

    def binding_execute(self, cmd: str, *args: tuple, **kwargs: dict[str, Any]):
        binding_command = self._conn.get_bindings.__getattribute__(cmd)
        if not isinstance(binding_command, Callable):
            raise TypeError(f"Command {cmd} is not an executable RTC6 binding!")
        binding_command(*args, **kwargs)


class RtcInfoController(ConnectedSubController):
    firmware_version = AttrR(Int(), group="Information")
    serial_number = AttrR(Int(), group="Information")
    ip_address = AttrR(String(), group="Information")
    is_acquired = AttrR(Bool(znam="False", onam="True"), group="Information")

    async def proc_cardinfo(self) -> None:
        info = self._conn.get_card_info()
        await asyncio.gather(
            self.firmware_version.set(info.firmware_version),
            self.serial_number.set(info.serial_number),
            self.ip_address.set(info.ip_address),
            self.is_acquired.set(info.is_acquired),
        )




class RtcControlSettings(ConnectedSubController):

    class LaserMode(StrEnum):
        CO2 = auto()
        YAG1 = auto()
        YAG2 = auto()
        YAG3 = auto()
        LASER4 = auto()
        YAG5 = auto()
        LASER = auto()

    @dataclass
    class ControlSettingsHandler(Sender):
        cmd: str

        async def put(self, controller: ConnectedSubController, attr: AttrW, value: Any):
            controller.binding_execute(self.cmd, value)

    # Page 645 of the manual
    laser_mode = AttrW(
        String(),
        group="LaserControl",
        allowed_values=[str(v).upper() for v in list(LaserMode)],
        handler=ControlSettingsHandler("set_laser_mode"),
    )
    jump_speed = AttrW(
        Float(),
        group="LaserControl",
        handler=ControlSettingsHandler("set_jump_speed_ctrl"),
    )  # set_jump_speed_ctrl
    mark_speed = AttrW(
        Float(),
        group="LaserControl",
        handler=ControlSettingsHandler("set_mark_speed_ctrl"),
    )  # set_mark_speed_ctrl
    # set_scanner_delays(jump, mark, polygon) in 10us increments
    jump_delay = AttrW(Int(), group="LaserControl",
        handler=ControlSettingsHandler("n_set_scanner_delays_ctrl"))
    mark_delay = AttrW(Int(), group="LaserControl",
        handler=ControlSettingsHandler("n_set_scanner_delays_ctrl"))
    polygon_delay = AttrW(Int(), group="LaserControl",
        handler=ControlSettingsHandler("n_set_scanner_delays_ctrl"))
    sky_writing_mode = AttrW(
        Int(),
        group="LaserControl",
        handler=ControlSettingsHandler("set_sky_writing_mode")
    )


class RtcListOperations(ConnectedSubController):
    list_pointer_position = AttrR(Int(), group="ListInfo")

    class AddJump(ConnectedSubController):
        x = AttrRW(Int(), group="ListOps")
        y = AttrRW(Int(), group="ListOps")

        @command(group="ListOps")
        async def proc(self):
            bindings = self._conn.get_bindings()
            bindings.add_jump_to(self.x.get(), self.y.get())

    class AddArc(ConnectedSubController):
        x = AttrRW(Int(), group="ListOps")
        y = AttrRW(Int(), group="ListOps")
        angle = AttrRW(Float(), group="ListOps")

        @command()
        async def proc(self):
            bindings = self._conn.get_bindings()
            bindings.add_arc_to(self.x.get(), self.y.get(), self.angle.get())

    class AddLine(ConnectedSubController):
        x = AttrRW(Int(), group="ListOps")
        y = AttrRW(Int(), group="ListOps")

        @command()
        async def proc(self):
            bindings = self._conn.get_bindings()
            bindings.add_line_to(self.x.get(), self.y.get())


class RtcController(Controller):
    def __init__(
        self,
        box_ip: str,
        program_file_dir: str,
        correction_file: str,
        retry_connect: bool = False,
    ) -> None:
        super().__init__()
        self._conn = RtcConnection(
            box_ip, program_file_dir, correction_file, retry_connect
        )
        self._info_controller = RtcInfoController(self._conn)
        self.register_sub_controller("INFO", self._info_controller)
        self.register_sub_controller("CONTROL", RtcControlSettings(self._conn))
        list_controller = RtcListOperations(self._conn)
        self.register_sub_controller("LIST", list_controller)
        list_controller.register_sub_controller(
            "ADDJUMP", list_controller.AddJump(self._conn)
        )
        list_controller.register_sub_controller(
            "ADDARC", list_controller.AddArc(self._conn)
        )
        list_controller.register_sub_controller(
            "ADDLINE", list_controller.AddLine(self._conn)
        )

    async def connect(self) -> None:
        await self._conn.connect()
        await self._info_controller.proc_cardinfo()

    async def close(self) -> None:
        await self._conn.close()
