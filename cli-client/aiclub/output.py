"""Shared Rich console and small output helpers."""

from __future__ import annotations

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def success(message: str) -> None:
    console.print(f"[bold green]✔[/] {message}")


def error(message: str) -> None:
    err_console.print(f"[bold red]✘[/] {message}")


def info(message: str) -> None:
    console.print(f"[cyan]•[/] {message}")


def mask(secret: str, show: int = 6) -> str:
    """Mask a secret for display, keeping the last few characters."""
    if not secret:
        return "(unset)"
    if len(secret) <= show:
        return "*" * len(secret)
    return "…" + secret[-show:]
