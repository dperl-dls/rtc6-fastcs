import subprocess
import sys

from rtc6_fastcs import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "rtc6_fastcs", "--version"]
    output = subprocess.check_output(cmd).decode().strip()
    assert output == __version__
