"""
Runtime path resolution — works both as script and as PyInstaller --onefile bundle.
When bundled, PyInstaller extracts files to sys._MEIPASS (temp dir).
"""
import os
import sys


def base_dir() -> str:
    """Returns the directory where bundled resources live."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tool_path(filename: str) -> str:
    """Full path to a tool executable."""
    return os.path.join(base_dir(), "tools", filename)


def config_path() -> str:
    """
    Config is writable → store next to the real .exe (not in temp MEIPASS).
    Falls back to AppData if exe dir is not writable.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    path = os.path.join(exe_dir, "config.json")

    # Test writability
    try:
        with open(path, "a"):
            pass
        return path
    except OSError:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        folder = os.path.join(appdata, "ElysiumChecker")
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, "config.json")
