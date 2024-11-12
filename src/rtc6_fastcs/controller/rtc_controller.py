import asyncio

from fastcs.attributes import AttrR
from fastcs.controller import Controller
from fastcs.datatypes import Bool, Int, String
from fastcs.wrappers import command

from rtc6_fastcs.controller.rtc_connection import RtcConnection


class RtcController(Controller):
    firmware_version = AttrR(Int(), group="Information")
    serial_number = AttrR(Int(), group="Information")
    ip_address = AttrR(String(), group="Information")
    is_acquired = AttrR(Bool(znam="False", onam="True"), group="Information")
    # TODO add handlers for these which proc cardinfo

    def __init__(self, box_ip: str, program_file: str, correction_file: str) -> None:
        super().__init__()
        self._conn = RtcConnection(box_ip, program_file, correction_file)

    async def connect(self) -> None:
        await self._conn.connect()

    async def close(self) -> None:
        await self._conn.close()

    @command()
    async def proc_cardinfo(self) -> None:
        info = self._conn.get_card_info()
        await asyncio.gather(
            self.firmware_version.set(info.firmware_version),
            self.serial_number.set(info.serial_number),
            self.ip_address.set(info.ip_address),
            self.is_acquired.set(info.is_acquired),
        )
