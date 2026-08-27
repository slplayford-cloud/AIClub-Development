"""Root Typer application and entrypoint for the aiclub CLI."""

from __future__ import annotations

import typer

from . import __version__
from .client import health_check
from .commands import auth, update as update_cmd
from .config import ConfigError, config_file, load_config
from .output import console, error, info, mask

app = typer.Typer(
    name="aiclub",
    help="CLI for the university AI & Machine Learning club.",
    no_args_is_help=True,
    add_completion=False,
)

# Account setup & verification (M1)
app.command()(auth.login)
app.command()(auth.whoami)
app.command()(auth.logout)

# Keep the tool current
app.command()(update_cmd.update)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"aiclub {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    _version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """AIClub CLI — verify membership, browse assignments/workshops, submit code."""


@app.command()
def status() -> None:
    """Show configuration and check the connection to Supabase."""
    try:
        cfg = load_config()
    except ConfigError as exc:
        error(str(exc))
        info(f"Config file location: {config_file()}")
        raise typer.Exit(code=1)

    console.print("[bold]aiclub configuration[/]")
    console.print(f"  Supabase URL   : {cfg.supabase_url}")
    console.print(f"  Anon key       : {mask(cfg.supabase_anon_key)}")
    console.print(f"  Allowed domain : @{cfg.allowed_domain}")

    info("Checking connection to Supabase…")
    try:
        health_check(cfg)
    except Exception as exc:  # noqa: BLE001 - surface any connection problem plainly
        error(f"Could not reach Supabase: {exc}")
        raise typer.Exit(code=1)

    console.print("[bold green]✔ Connected to Supabase.[/]")


def main() -> None:
    """Console-script entrypoint."""
    app()


if __name__ == "__main__":
    main()
