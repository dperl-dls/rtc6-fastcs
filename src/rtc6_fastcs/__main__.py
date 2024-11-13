import subprocess
from functools import cache
from pathlib import Path

import typer

from rtc6_fastcs.controller import RtcController

from . import __version__

__all__ = ["main"]


app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    ),
):
    pass


@app.command()
def install_library():
    subprocess.call(
        ["bash", "/workspaces/rtc6-controller/src/rtc6_fastcs/install_library.sh"]
    )


@app.command()
def ioc(
    pv_prefix: str = typer.Argument("RTC6ETH", help="Name of the IOC"),
    box_ip: str = typer.Argument("172.23.17.192", help="IP Address of the RTC6 ethbox"),
    program_file_dir: str = typer.Argument(
        "./rtc6_files/program_files", help="Path to the RTC6 program files"
    ),
    correction_file: str = typer.Argument(
        "./rtc6_files/correction_files/Cor_1to1.ct5",
        help="Path to the RTC6 correction file",
    ),
    retry_connect: bool = typer.Option(
        False,
        help="Retry connecting to the RTC6 if the initial attempt fails",
    ),
    output_path: Path = typer.Option(  # noqa: B008
        Path.cwd(),  # noqa: B008
        help="folder of local service definition",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
):
    """
    Start up the service
    """
    from fastcs.backends.epics.backend import EpicsBackend, EpicsGUIOptions

    backend = EpicsBackend(
        get_controller(box_ip, program_file_dir, correction_file, retry_connect),
        pv_prefix,
    )
    backend.create_gui(EpicsGUIOptions(output_path / "index.bob"))
    backend.run()


@cache
def get_controller(
    box_ip: str, program_file: str, correction_file: str, retry_connect: bool
) -> RtcController:
    return RtcController(box_ip, program_file, correction_file, retry_connect)


if __name__ == "__main__":
    app()
