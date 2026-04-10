import os
import string
from datetime import datetime

# Signatures — known cheat-related names
SIGNATURES = [
    # Specific CS2/CSGO cheat clients
    "skeet", "sk33t", "skeet.cc", "fatality", "fatality.win", "neverlose", "neverlose.cc",
    "gamesense", "aimware", "onetap", "nixware", "midnight", "primordial",
    "memesense", "anyx", "projectinfinity", "legendware", "uranium", "osiris",
    "interwebz", "lucid", "es3", "xone", "midnight", "xoneware", "hvh", "hvhcheat", "streamproof",
    "legitcheat", "ragehack", "ragebot", "compkiller", "astral", "astral.rip",
    "venom", "britva", "pena", "axion", "plague", "plaguecheat", "enigma",
    "en1gma", "vredux", "vrx", "asphyxia", "mezware", "magichka",
    "geraengine", "gripix", "grapeRage", "extrimhack", "multihack",
    "zrk", "zrk menu", "weave", "dragonhack", "wraith", "chieftain", "mason",
    "nova macro", "predator", "predator.systems", "luno", "sharkhack", "sharkhack.fun",
    "legitbot", "aimbot", "wallhack", "triggerbot", "spinbot",
    "antiaimbot", "antiaim", "bunnyhop", "bhop", "speedhack",
    "noclip", "autofire", "autoshoot", "esp_", "_esp",
    "no-recoil", "norecoil", "recoil_script",
    "skinchanger", "skin_changer", "skinswapper", "inventorychanger",
    "exloader", "exclient",
    # Generic cheat / crack / injection
    "crack", "cracked", "crackme",
    "injector", "inject", "dll_inject", "dllinjector",
    "loader", "cheatloader", "cheat_loader",
    "bypass", "anticheat_bypass", "vac_bypass", "eac_bypass",
    "cheat", "cheats", "cheating",
    "hack", "hacks", "hacked", "hacking",
    "trainer", "gamehack", "gamecheat",
    "keygen", "keygenme",
    # Specific tools / RATs / suspiciously named
    "memhack", "memoryhack", "memreader",
    "externalhack", "internalhack",
    "d3dhook", "d3d_hook",
    "openglhook", "vulkanhook",
    "gameguard_bypass", "be_bypass", "easy_anti",
    # HvH / scene specific
    "hotvshot", "hvh_config", "rage_config",
    "legitaa", "legit",
    "backtrack", "back_track",
    "doubletap", "dt_config",
    "autowall", "auto_wall",
    "resolverbypass",
   # Common cheat config / log folders
"cheatconfig", "cheat_config",
"cheat_settings", "cheat_menu",
"cheat_log", "cheat_logs",
"aimconfig", "aim_config",
"hvhconfig", "hvh_config",

# Lua / scripts (у большинства читов есть lua api)
"lua_scripts", "cheat_lua", "autoexec_cheat",
"skeet_lua", "nl_lua", "fatality_lua",

# Inject / loader folders
"inject", "injector", "loader",
"cheat_loader", "cheatloader",
"dll_inject", "dllinjector",

# Bypass / anticheat
"vac_bypass", "eac_bypass", "anticheat_bypass",
"trustfactor", "trust_bypass",

# Config dumps / exports типичные для читов
"rage_cfg", "legit_cfg", "hvh_cfg",
"semirageconfig", "semirage_cfg",
"nospread_cfg", "spread_cfg",

# DMA (железные читы, популярно в СНГ)
"dma_cheat", "dma_esp", "dma_hack",

# Misc папки которые создают читы
"cheat_data", "cheat_cache",
"skinsettings", "skin_settings",
"skinconfig", "skin_cfg",
]

# Convert to lowercase set for fast lookup
SIGNATURES = list({s.lower() for s in SIGNATURES})


def _get_drives() -> list[str]:
    drives = []
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            drives.append(path)
    return drives


def scan_all_drives(
    progress_callback=None,   # callable(files_count, folders_count, current_path)
    result_callback=None,     # callable(item_dict) — called for each match
    stop_event=None           # threading.Event to abort
) -> list[dict]:
    results = []
    files_count = 0
    folders_count = 0

    drives = _get_drives()

    for drive in drives:
        if stop_event and stop_event.is_set():
            break
        try:
            for root, dirs, files in os.walk(drive, topdown=True):
                if stop_event and stop_event.is_set():
                    break

                # Skip system dirs for performance
                dirs[:] = [
                    d for d in dirs
                    if d not in (
                        "Windows", "System32", "SysWOW64", "WinSxS",
                        "$Recycle.Bin", "Recovery", "ProgramData\\Microsoft",
                    )
                ]

                folders_count += len(dirs)
                files_count += len(files)

                if progress_callback:
                    progress_callback(files_count, folders_count, root)

                # Check folders
                for name in dirs:
                    if _matches(name):
                        path = os.path.join(root, name)
                        item = _make_item(name, path, is_file=False)
                        results.append(item)
                        if result_callback:
                            result_callback(item)

                # Check files
                for name in files:
                    if _matches(name):
                        path = os.path.join(root, name)
                        item = _make_item(name, path, is_file=True)
                        results.append(item)
                        if result_callback:
                            result_callback(item)

        except PermissionError:
            continue
        except Exception:
            continue

    results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return results


def _matches(name: str) -> bool:
    name_lower = name.lower()
    for sig in SIGNATURES:
        if sig in name_lower:
            return True
    return False


def _make_item(name: str, path: str, is_file: bool) -> dict:
    try:
        ts = os.path.getmtime(path)
        date_str = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
    except Exception:
        ts = 0
        date_str = "Неизвестно"

    return {
        "name": name,
        "path": path,
        "type": "Файл" if is_file else "Папка",
        "date": date_str,
        "timestamp": ts,
    }
