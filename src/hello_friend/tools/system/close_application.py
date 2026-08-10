"""
Close a desktop application.

This is intentionally conservative. Closing applications can cause
unsaved work to be lost, so this tool should eventually be protected
by an approval/policy step in the LangGraph agent.
"""

import logging
import platform
import subprocess

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def close_application(name: str) -> str:
    """
    Close a desktop application by process/application name.

    Use this only when the user explicitly asks to close an application.

    Warning: closing an application may cause unsaved work to be lost.
    """
    name = name.strip()

    if not name:
        return "Error: application name is required."

    system = platform.system()

    try:
        if system == "Windows":
            result = subprocess.run(
                ["taskkill", "/IM", name, "/T"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        elif system == "Darwin":
            result = subprocess.run(
                ["osascript", "-e", f'tell application "{name}" to quit'],
                capture_output=True,
                text=True,
                timeout=10,
            )

        elif system == "Linux":
            result = subprocess.run(
                ["pkill", "-x", name],
                capture_output=True,
                text=True,
                timeout=10,
            )

        else:
            return f"Error: unsupported operating system '{system}'."

        if result.returncode != 0:
            error = result.stderr.strip() or "application was not found"
            return f"Error: could not close '{name}': {error}"

        return f"Closed application '{name}'."

    except subprocess.TimeoutExpired:
        return f"Error: timed out while trying to close '{name}'."

    except (FileNotFoundError, OSError) as exc:
        logger.exception("Failed to close application: %s", name)
        return f"Error: could not close '{name}': {exc}"

    except Exception as exc:
        logger.exception("Unexpected error closing application: %s", name)
        return f"Error: could not close '{name}': {exc}"