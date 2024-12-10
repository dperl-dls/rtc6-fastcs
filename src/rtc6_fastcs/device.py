from ophyd_async.core import StandardReadable, AsyncStageable
from bluesky.protocols import Triggerable
from ophyd_async.epics.core import (
    epics_signal_rw,
    epics_signal_r,
    epics_signal_x,
    epics_signal_w,
)
from ophyd_async.core import AsyncStatus


class Rtc6ControlSettings(StandardReadable):
    def __init__(self, prefix: str = "CONTROL:", name: str = "") -> None:
        super().__init__(name)
        with self.add_children_as_readables():
            # TODO: make a python Enum to match the c++ enum so that we can limit this to the allowed values
            self.laser_mode = epics_signal_rw(str, prefix + "LaserMode")
            # This should be split up and made nicer if it is every really used, but currently is always just set to 0
            self.laser_control = epics_signal_rw(int, prefix + "LaserControl")
            self.jump_speed = epics_signal_rw(float, prefix + "JumpSpeed")
            self.mark_speed = epics_signal_rw(float, prefix + "MarkSpeed")
            self.jump_delay = epics_signal_rw(int, prefix + "JumpDelay")
            self.mark_delay = epics_signal_rw(int, prefix + "MarkDelay")
            self.polygon_delay = epics_signal_rw(int, prefix + "PolygonDelay")


class Rtc6Info(StandardReadable):
    def __init__(self, prefix: str = "INFO:", name: str = "") -> None:
        super().__init__(name)
        with self.add_children_as_readables():
            self.firmware_version = epics_signal_r(int, prefix + "FirmwareVersion")
            self.serial_number = epics_signal_r(int, prefix + "SerialNumber")
            self.ip_address = epics_signal_r(str, prefix + "IpAddress")
            self.is_acquired = epics_signal_r(str, prefix + "IsAcquired")


class Rtc6List(StandardReadable):
    class AddArc(StandardReadable):
        def __init__(self, prefix: str = "ADDARC:", name: str = "") -> None:
            """Used for `arc_abs`, manual page 314"""
            super().__init__(name)
            with self.add_children_as_readables():
                self.x = epics_signal_w(int, prefix + "X")
                self.y = epics_signal_w(int, prefix + "Y")
                self.angle_deg = epics_signal_w(float, prefix + "Angle")
                self.proc = epics_signal_x(prefix + "Proc")

    class AddLine(StandardReadable):
        def __init__(self, prefix: str = "ADDLINE:", name: str = "") -> None:
            """Used for `arc_abs`, manual page 314"""
            super().__init__(name)
            with self.add_children_as_readables():
                self.x = epics_signal_w(int, prefix + "X")
                self.y = epics_signal_w(int, prefix + "Y")
                self.proc = epics_signal_x(prefix + "Proc")

    class AddJump(StandardReadable):
        def __init__(self, prefix: str = "ADDJUMP:", name: str = "") -> None:
            """Used for `arc_abs`, manual page 314"""
            super().__init__(name)
            with self.add_children_as_readables():
                self.x = epics_signal_w(int, prefix + "X")
                self.y = epics_signal_w(int, prefix + "Y")
                self.proc = epics_signal_x(prefix + "Proc")

    def __init__(self, prefix: str = "LIST:", name: str = "") -> None:
        super().__init__(name)
        with self.add_children_as_readables():
            self.add_arc = self.AddArc(prefix + "ADDARC:")
            self.add_line = self.AddLine(prefix + "ADDLINE:")
            self.add_jump = self.AddJump(prefix + "ADDJUMP:")
            self.init_list = epics_signal_x(prefix + "InitList")
            self.end_list = epics_signal_x(prefix + "EndList")
            self.execute_list = epics_signal_x(prefix + "ExecuteList")


class Rtc6Eth(StandardReadable, AsyncStageable, Triggerable):
    def __init__(self, prefix: str = "RTC6ETH:", name: str = "") -> None:
        super().__init__(name)
        with self.add_children_as_readables():
            self.info = Rtc6Info(prefix + "INFO:")
            self.control_settings = Rtc6ControlSettings(prefix + "CONTROL:")
            self.list = Rtc6List(prefix + "LIST:")

    @AsyncStatus.wrap
    async def stage(self):
        """Set things up to start writing list commands"""
        await self.control_settings.laser_mode.set("YAG5")
        await self.control_settings.laser_control.set(0)
        await self.list.init_list.trigger()

    @AsyncStatus.wrap
    async def trigger(self):
        """Set the end of the list at the current position and set it to execute"""
        await self.list.end_list.trigger()
        await self.list.execute_list.trigger()

    @AsyncStatus.wrap
    async def complete(self):
        """Wait for the current list execution to complete"""
        # Todo add a signal for this with get_status
        # and change trigger to kickoff

    @AsyncStatus.wrap
    async def unstage(self): ...
