import subprocess
from functools import cache
from pathlib import Path
from typing import Annotated

import typer

from rtc6_fastcs.controller import RtcController

from . import __version__

__all__ = ["main"]

CWD_AT_LOADING = Path.cwd()
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
        ["bash", "/workspace/rtc6-controller/src/rtc6_fastcs/install_library.sh"]
    )


@app.command()
def ioc(
    pv_prefix: Annotated[str, typer.Argument(help="Name of the IOC")] = "RTC6ETH",
    box_ip: Annotated[
        str, typer.Argument(help="IP Address of the RTC6 ethbox")
    ] = "172.23.17.192",
    program_file_dir: Annotated[
        str, typer.Argument(help="Path to the directory of the RTC6 program files")
    ] = "./rtc6_files/program_files",
    correction_file: Annotated[
        str,
        typer.Argument(
            help="Path to the RTC6 correction file",
        ),
    ] = "./rtc6_files/correction_files/Cor_1to1.ct5",
    retry_connect: Annotated[
        bool,
        typer.Option(
            help="Retry connecting to the RTC6 if the initial attempt fails",
        ),
    ] = False,
    output_path: Annotated[
        Path,
        typer.Option(
            help="folder of local service definition",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ] = CWD_AT_LOADING,
):
    """
    Start up the service
    """
    from fastcs.backends.epics.backend import (
        EpicsBackend,
        EpicsDocsOptions,
        EpicsGUIOptions,
    )

    backend = EpicsBackend(
        get_controller(box_ip, program_file_dir, correction_file, retry_connect),
        pv_prefix,
    )
    backend.create_docs(EpicsDocsOptions(output_path / "index.md"))
    backend.create_gui(EpicsGUIOptions(output_path / "index.bob"))
    backend.run()


@cache
def get_controller(
    box_ip: str, program_file: str, correction_file: str, retry_connect: bool
) -> RtcController:
    return RtcController(box_ip, program_file, correction_file, retry_connect)


if __name__ == "__main__":
    app()
