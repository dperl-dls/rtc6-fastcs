from fastcs.controller import Controller

from rtc6_fastcs.controller.rtc_connection import RtcConnection


class RtcController(Controller):
    def __init__(self, box_ip: str, program_file: str, correction_file: str) -> None:
        super().__init__()
        self._conn = RtcConnection(box_ip, program_file, correction_file)

    async def connect(self) -> None:
        await self._conn.connect()

    async def close(self) -> None:
        await self._conn.close()
