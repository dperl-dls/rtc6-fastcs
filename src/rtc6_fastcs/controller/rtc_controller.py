import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastcs.attributes import AttrR, AttrW, AttrRW, Sender
from fastcs.controller import Controller, SubController
from fastcs.datatypes import Bool, Float, Int, String
from fastcs.wrappers import command

from py import process
from rtc6_fastcs.controller.rtc_connection import RtcConnection
from rtc6_fastcs.bindings import rtc6_bindings as rtc6


class ConnectedSubController(SubController):
    def __init__(self, conn: RtcConnection) -> None:
        super().__init__()
        self._conn = conn


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
    @dataclass
    class ControlSettingsHandler(Sender):
        cmd: Callable

        async def put(
            self, controller: ConnectedSubController, attr: AttrW, value: Any
        ):
            self.cmd(value)

    @dataclass
    class DelaysHandler(Sender):
        update_period = 0.0

        async def put(self, controller: "RtcControlSettings", attr: AttrW, value: Any):
            rtc6.set_scanner_delays(
                controller.jump_delay.get(),
                controller.mark_delay.get(),
                controller.polygon_delay.get(),
            )

        async def update(self, controller: "RtcControlSettings", attr: AttrR): ...

    # Page 645 of the manual
    laser_mode = AttrW(
        String(),
        group="LaserControl",
        allowed_values=[rtc6.LaserMode(i).name for i in range(7)],
        handler=ControlSettingsHandler(rtc6.set_laser_mode),
    )
    laser_control = AttrW(
        Int(),
        group="LaserControl",
        handler=ControlSettingsHandler(rtc6.set_laser_control),
    )
    jump_speed = AttrW(
        Float(),
        group="LaserControl",
        handler=ControlSettingsHandler(rtc6.set_mark_speed_ctrl),
    )  # set_jump_speed_ctrl
    mark_speed = AttrW(
        Float(),
        group="LaserControl",
        handler=ControlSettingsHandler(rtc6.set_jump_speed_ctrl),
    )  # set_mark_speed_ctrl
    # set_scanner_delays(jump, mark, polygon) in 10us increments
    # need to all be set at once - special handler
    jump_delay = AttrRW(
        Int(),
        group="LaserControl",
        handler=DelaysHandler(),
    )
    mark_delay = AttrRW(
        Int(),
        group="LaserControl",
        handler=DelaysHandler(),
    )
    polygon_delay = AttrRW(
        Int(),
        group="LaserControl",
        handler=DelaysHandler(),
    )
    sky_writing_mode = AttrW(
        Int(),
        group="LaserControl",
        handler=ControlSettingsHandler(rtc6.set_sky_writing_mode),
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

    @command()
    async def init_list(self):
        rtc6 = self._conn.get_bindings()
        rtc6.config_list_memory(-1, 0)  # Just put everything on list one
        rtc6.init_list_loading(1)

    @command()
    async def end_list(self):
        rtc6 = self._conn.get_bindings()
        rtc6.set_end_of_list()

    @command()
    async def execute_list(self):
        rtc6 = self._conn.get_bindings()
        rtc6.execute_list(1)


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
