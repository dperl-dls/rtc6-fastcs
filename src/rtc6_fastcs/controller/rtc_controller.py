import asyncio
from dataclasses import dataclass

from fastcs.attributes import AttrR
from fastcs.controller import Controller, SubController
from fastcs.datatypes import Bool, Int, String
from fastcs.wrappers import command

from rtc6_fastcs.bindings.rtc6_bindings import CardInfo
from rtc6_fastcs.controller.rtc_connection import RtcConnection


class RtcInfoController(SubController):
    @dataclass
    class InfoHandler:
        # TODO improve this ugly cache, or remove and just add the update to connect()
        update_period = 1.0
        cache: CardInfo | None = None

        async def update(self, controller: "RtcInfoController", attr: AttrR):
            if self.cache is None:
                self.cache = await controller.proc_cardinfo()
                print("updating card info")

    firmware_version = AttrR(Int(), handler=InfoHandler(), group="Information")
    serial_number = AttrR(Int(), handler=InfoHandler(), group="Information")
    ip_address = AttrR(String(), handler=InfoHandler(), group="Information")
    is_acquired = AttrR(
        Bool(znam="False", onam="True"), handler=InfoHandler(), group="Information"
    )

    async def proc_cardinfo(self) -> CardInfo:
        info = self._conn.get_card_info()
        await asyncio.gather(
            self.firmware_version.set(info.firmware_version),
            self.serial_number.set(info.serial_number),
            self.ip_address.set(info.ip_address),
            self.is_acquired.set(info.is_acquired),
        )
        return info

    def __init__(self, conn: RtcConnection) -> None:
        super().__init__()
        self._conn = conn


class RtcController(Controller):
    def __init__(self, box_ip: str, program_file: str, correction_file: str) -> None:
        super().__init__()
        self._conn = RtcConnection(box_ip, program_file, correction_file)
        self.register_sub_controller("INFO", RtcInfoController(self._conn))

    async def connect(self) -> None:
        await self._conn.connect()

    async def close(self) -> None:
        await self._conn.close()
