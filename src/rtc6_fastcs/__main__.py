import logging
import subprocess
from functools import cache
from pathlib import Path
from typing import Annotated
from fastcs.launch import FastCS

from fastcs.backend import Backend
import typer
from fastcs.transport.epics.options import EpicsIOCOptions, EpicsOptions

from rtc6_fastcs.controller import RtcController

from . import __version__

LOGGER = logging.getLogger(__name__)

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


def create_ui_and_docs(controller: RtcController, prefix: str, output_path: Path):
    from fastcs.transport.epics.gui import EpicsGUI, EpicsGUIOptions
    from fastcs.transport.epics.docs import EpicsDocs, EpicsDocsOptions

    gui = EpicsGUI(controller, prefix)
    gui.create_gui(EpicsGUIOptions(output_path / "index.bob"))
    docs = EpicsDocs(controller)
    docs.create_docs(EpicsDocsOptions(output_path / "index.md"))


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
    ] = "./correction_files/D2_2034.ct5",
    coordinate_system_correction_file: Annotated[
        str,
        typer.Argument(
            help="path to a numpy matrix to use to correct the coordinate system",
        ),
    ] = "./correction_files/coord_transform",
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

    controller = get_controller(
        box_ip,
        program_file_dir,
        correction_file,
        coordinate_system_correction_file,
        retry_connect,
    )
    create_ui_and_docs(controller, pv_prefix, output_path)

    epics_options = EpicsOptions(ioc=EpicsIOCOptions(pv_prefix=pv_prefix))
    fastcs = FastCS(controller, epics_options)
    fastcs.run()


@cache
def get_controller(
    box_ip: str,
    program_file: str,
    correction_file: str,
    coordinate_system_correction_file: str,
    retry_connect: bool,
) -> RtcController:
    return RtcController(
        box_ip,
        program_file,
        correction_file,
        coordinate_system_correction_file,
        retry_connect,
    )


if __name__ == "__main__":
    app()
