from rtc6_fastcs.bindings.rtc6_bindings import CardInfo


class RtcConnection:
    def __init__(self, box_ip: str, program_file: str, correction_file: str) -> None:
        from rtc6_fastcs.bindings import rtc6_bindings as bindings

        self._bindings = bindings
        self._ip = box_ip
        self._program_file = program_file
        self._correction_file = correction_file

    def get_card_info(self) -> CardInfo:
        return self._bindings.get_card_info()

    async def connect(self) -> None:
        self._bindings.connect(self._ip, self._program_file, self._correction_file)

    async def close(self) -> None:
        self._bindings.close()
