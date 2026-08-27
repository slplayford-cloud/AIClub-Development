"""Self-update: pull the latest aiclub from GitHub via uv.

`aiclub update` shells out to `uv` (the tool that installed aiclub) so members
never have to remember the install command.

We use `uv tool install --force <git-url>` rather than `uv tool upgrade`, because
`upgrade` only acts when the package *version number* changes — it's a no-op when
we ship new code under the same version. A forced install always reinstalls from
the latest commit on the repo, so `aiclub update` reliably pulls the newest code.
"""

from __future__ import annotations

import shutil
import subprocess

import typer

from .. import __version__
from ..output import console, error, info, success

# Canonical install source. Keep in sync with README / docs/AUTH_SETUP.md.
GIT_SOURCE = (
    "git+https://github.com/slplayford-cloud/AIClub-Development"
    "#subdirectory=cli-client"
)


def update() -> None:
    """Update aiclub to the latest version from GitHub."""
    uv = shutil.which("uv")
    if uv is None:
        error("Couldn't find `uv` on your PATH — aiclub is installed with uv.")
        info("Install uv (https://docs.astral.sh/uv/) and try again.")
        raise typer.Exit(code=1)

    cmd = [uv, "tool", "install", "--force", GIT_SOURCE]

    info(f"Current version: {__version__}")
    info("Fetching the latest aiclub from GitHub …")
    console.print(f"[dim]$ {' '.join(cmd)}[/]")

    result = subprocess.run(cmd)  # stream uv's output straight to the terminal
    if result.returncode != 0:
        error("Update failed. Check your internet connection and try again.")
        raise typer.Exit(code=result.returncode)

    success("aiclub is up to date. Re-run your command to use the new version.")
