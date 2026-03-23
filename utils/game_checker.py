"""
Game check: find CS2 process, focus its window, send key presses via SendInput.
Uses ctypes only — no pywin32 dependency for key sending.
"""
import ctypes
import ctypes.wintypes
import time

try:
    import psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False

try:
    import win32gui
    import win32process
    _WIN32_OK = True
except ImportError:
    _WIN32_OK = False


CS2_PROCESS_NAME = "cs2.exe"
KEY_DELAY = 0.4   # seconds between keys

# Virtual key codes for common cheat menu binds
CHEAT_KEYS = [
    (0x2D, "INSERT"),
    (0x2E, "DELETE"),
    (0x24, "HOME"),
    (0x23, "END"),
    (0x21, "PAGE UP"),
    (0x22, "PAGE DOWN"),
    (0x70, "F1"),
    (0x71, "F2"),
    (0x72, "F3"),
    (0x73, "F4"),
    (0x74, "F5"),
    (0x75, "F6"),
    (0x76, "F7"),
    (0x77, "F8"),
    (0x78, "F9"),
    (0x79, "F10"),
    (0x7A, "F11"),
    (0x7B, "F12"),
    (0xC0, "~ (TILDE)"),
    (0x60, "NUMPAD 0"),
    (0x61, "NUMPAD 1"),
    (0x62, "NUMPAD 2"),
    (0x63, "NUMPAD 3"),
    (0x64, "NUMPAD 4"),
    (0x65, "NUMPAD 5"),
    (0x66, "NUMPAD 6"),
    (0x67, "NUMPAD 7"),
    (0x68, "NUMPAD 8"),
    (0x69, "NUMPAD 9"),
]


KEYEVENTF_KEYUP = 0x0002

_user32   = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

# keybd_event — deprecated but dead-simple and reliable
_keybd_event = _user32.keybd_event
_keybd_event.argtypes = [
    ctypes.c_ubyte,   # bVk
    ctypes.c_ubyte,   # bScan
    ctypes.c_uint,    # dwFlags
    ctypes.c_size_t,  # dwExtraInfo
]
_keybd_event.restype = None


def _send_vk(vk: int):
    _keybd_event(vk, 0, 0,               0)  # key down
    time.sleep(0.06)
    _keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)  # key up


def _focus_window(hwnd: int):
    """
    Force CS2 to foreground. AttachThreadInput pattern:
    attach OUR thread to the current foreground thread → then
    SetForegroundWindow is no longer blocked by Windows.
    """
    SW_RESTORE = 9

    fg_hwnd  = _user32.GetForegroundWindow()
    fg_tid   = _user32.GetWindowThreadProcessId(fg_hwnd, None)
    our_tid  = _kernel32.GetCurrentThreadId()

    attached = False
    if fg_tid and fg_tid != our_tid:
        attached = _user32.AttachThreadInput(our_tid, fg_tid, True)

    _user32.ShowWindow(hwnd, SW_RESTORE)
    _user32.BringWindowToTop(hwnd)
    _user32.SetForegroundWindow(hwnd)
    _user32.SetFocus(hwnd)

    if attached:
        _user32.AttachThreadInput(our_tid, fg_tid, False)

    time.sleep(0.3)


# ------------------------------------------------------------------
# Process / window helpers
# ------------------------------------------------------------------

def is_cs2_running() -> bool:
    if not _PSUTIL_OK:
        return False
    try:
        for proc in psutil.process_iter(["name"]):
            if (proc.info.get("name") or "").lower() == CS2_PROCESS_NAME:
                return True
    except Exception:
        pass
    return False


def find_cs2_hwnd() -> int | None:
    """Returns HWND of the CS2 game window or None."""
    if not _PSUTIL_OK:
        return None

    # Collect CS2 PIDs
    cs2_pids: set[int] = set()
    try:
        for proc in psutil.process_iter(["name", "pid"]):
            if (proc.info.get("name") or "").lower() == CS2_PROCESS_NAME:
                cs2_pids.add(proc.info["pid"])
    except Exception:
        pass

    if not cs2_pids:
        return None

    if _WIN32_OK:
        result: list[int] = []

        def _cb(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in cs2_pids and win32gui.GetWindowText(hwnd):
                    result.append(hwnd)
                    return False
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_cb, None)
        except Exception:
            pass

        return result[0] if result else None

    # Fallback via ctypes EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    found = ctypes.wintypes.HWND(0)

    def _cb_ct(hwnd, _):
        if not ctypes.windll.user32.IsWindowVisible(hwnd):
            return True
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in cs2_pids:
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
            if buf.value:
                found.value = hwnd
                return False
        return True

    try:
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(_cb_ct), 0)
    except Exception:
        pass

    return found.value or None


def focus_cs2(hwnd: int):
    """Call once before starting key sequence."""
    try:
        _focus_window(hwnd)
    except Exception:
        pass


def send_key(hwnd: int, vk: int):
    """Send one key press (window must already be focused via focus_cs2)."""
    try:
        _send_vk(vk)
    except Exception:
        pass
