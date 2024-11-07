import subprocess

import typer

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


if __name__ == "__main__":
    app()
