import asyncio
import logging

from rtc6_fastcs.bindings.rtc6_bindings import CardInfo, RtcError

LOGGER = logging.getLogger(__name__)


class RtcConnection:
    def __init__(
        self,
        box_ip: str,
        program_file: str,
        correction_file: str,
        retry_connect: bool = False,
    ) -> None:
        from rtc6_fastcs.bindings import rtc6_bindings as bindings

        self._bindings = bindings
        self._ip = box_ip
        self._program_file = program_file
        self._correction_file = correction_file
        self._retry_connect = retry_connect

    def set_retry_connect(self, value: bool):
        self._retry_connect = value

    def get_card_info(self) -> CardInfo:
        return self._bindings.get_card_info()

    def get_bindings(self):
        return self._bindings

    async def connect(self) -> None:
        connected = 0
        while not connected:
            try:
                connected = self._bindings.connect(
                    self._ip, self._program_file, self._correction_file
                )
            except RtcError as e:
                if not self._retry_connect:
                    raise Exception("Not retrying failed connection") from e
                LOGGER.warning(f"Connection failed: {e.args[0]}! Retrying...")
                await asyncio.sleep(1)

    async def close(self) -> None:
        self._bindings.close()
