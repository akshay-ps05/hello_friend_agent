"""
Open a desktop application.

Provides friendly application names for common Windows applications
and uses platform-specific launching methods.

The LLM can say "calculator" instead of needing to know
"calc.exe".
"""

import logging
import os
import platform
import shutil
import subprocess

from langchain.tools import tool

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Common Windows application aliases
# ---------------------------------------------------------------------

WINDOWS_APPS = {
    "calculator": "calc.exe",
    "calc": "calc.exe",

    "notepad": "notepad.exe",

    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",

    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",

    "powershell": "powershell.exe",
    "power shell": "powershell.exe",

    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",

    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",

    "control panel": "control.exe",
}


@tool
def open_application(name: str) -> str:
    """
    Open a desktop application by name.

    Examples:
        calculator
        notepad
        paint
        powershell
        file explorer

    Use this only when the user explicitly asks to open an application.
    """

    name = name.strip()

    if not name:
        return "Error: application name is required."

    system = platform.system()

    try:
        if system == "Windows":
            return _open_windows_application(name)

        if system == "Darwin":
            return _open_macos_application(name)

        if system == "Linux":
            return _open_linux_application(name)

        return (
            f"Error: unsupported operating system '{system}'."
        )

    except subprocess.TimeoutExpired:
        return (
            f"Error: timed out while trying to open '{name}'."
        )

    except FileNotFoundError:
        return (
            f"Error: application '{name}' was not found."
        )

    except OSError as exc:
        logger.exception(
            "Failed to open application: %s",
            name,
        )
        return (
            f"Error: could not open '{name}': {exc}"
        )

    except Exception as exc:
        logger.exception(
            "Unexpected error opening application: %s",
            name,
        )
        return (
            f"Error: could not open '{name}': {exc}"
        )


def _open_windows_application(name: str) -> str:
    """Open an application on Windows."""

    normalized = name.lower().strip()

    # --------------------------------------------------------------
    # 1. Friendly application aliases
    # --------------------------------------------------------------

    executable = WINDOWS_APPS.get(normalized)

    if executable:
        subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return f"Opened application '{name}'."


    # --------------------------------------------------------------
    # 2. Exact executable/path
    # --------------------------------------------------------------

    if os.path.exists(name):
        os.startfile(name)  # type: ignore[attr-defined]
        return f"Opened application '{name}'."


    # --------------------------------------------------------------
    # 3. Executable available on PATH
    # --------------------------------------------------------------

    executable_path = shutil.which(name)

    if executable_path:
        subprocess.Popen(
            [executable_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return f"Opened application '{name}'."


    # --------------------------------------------------------------
    # 4. Try adding .exe
    # --------------------------------------------------------------

    if not normalized.endswith(".exe"):
        executable_path = shutil.which(
            f"{normalized}.exe"
        )

        if executable_path:
            subprocess.Popen(
                [executable_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return f"Opened application '{name}'."


    return (
        f"Error: application '{name}' was not found. "
        f"Try using the application's executable name."
    )


def _open_macos_application(name: str) -> str:
    """Open an application on macOS."""

    subprocess.Popen(
        ["open", "-a", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"Opened application '{name}'."


def _open_linux_application(name: str) -> str:
    """Open an application on Linux."""

    executable = shutil.which(name)

    if not executable:
        raise FileNotFoundError(name)

    subprocess.Popen(
        [executable],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"Opened application '{name}'."