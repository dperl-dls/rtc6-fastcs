class RtcConnection:
    def __init__(self, box_ip: str) -> None:
        from rtc6_fastcs.bindings import rtc6_bindings as bindings

        self._bindings = bindings
        self._ip = box_ip

    async def connect(self) -> None:
        self._bindings.connect(self._ip)

    async def close(self) -> None:
        self._bindings.close()
