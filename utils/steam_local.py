"""
Reads Steam accounts from the local PC and fetches public profile data.
No API key required — uses Steam's public XML profile endpoint.

Sources (merged & deduplicated):
  1. config/loginusers.vdf  — accounts with "RememberPassword"
  2. userdata/<accountid>/  — ALL accounts that ever used this Steam install
  3. HKCU registry          — additional account IDs Valve stores there
"""
import os
import re
import winreg
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

STEAMID64_BASE = 76561197960265728


# ------------------------------------------------------------------
# Steam installation
# ------------------------------------------------------------------

def find_steam_path() -> str | None:
    reg_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Valve\Steam"),
    ]
    for hive, subkey in reg_keys:
        try:
            key = winreg.OpenKey(hive, subkey)
            path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
            if os.path.isdir(path):
                return path
        except Exception:
            continue

    for p in [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"D:\Steam",
        r"D:\Program Files (x86)\Steam",
        r"E:\Steam",
    ]:
        if os.path.isdir(p):
            return p

    return None


# ------------------------------------------------------------------
# VDF parser (state-machine, handles any nesting)
# ------------------------------------------------------------------

def _parse_vdf_block(text: str) -> dict:
    """Parse a flat VDF key-value block into a dict."""
    result = {}
    for m in re.finditer(r'"([^"\\]*)"\s+"([^"\\]*)"', text):
        result[m.group(1)] = m.group(2)
    return result


def _iter_top_blocks(content: str):
    """
    Yields (key, block_content) for each top-level "key" { ... } in the VDF.
    Uses a brace-counter so nested braces don't break parsing.
    """
    i = 0
    n = len(content)
    while i < n:
        # find next quoted key
        km = re.search(r'"([^"]*)"', content[i:])
        if not km:
            break
        key = km.group(1)
        i += km.end()

        # skip whitespace to find opening brace
        bm = re.search(r'\S', content[i:])
        if not bm or content[i + bm.start()] != '{':
            continue
        i += bm.start() + 1  # skip '{'

        depth = 1
        start = i
        while i < n and depth:
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
            i += 1

        yield key, content[start:i - 1]


# ------------------------------------------------------------------
# Source 1: loginusers.vdf
# ------------------------------------------------------------------

def _parse_loginusers(steam_path: str) -> dict[str, dict]:
    """Returns {steamid64_str: account_dict}"""
    vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
    accounts = {}
    if not os.path.isfile(vdf_path):
        return accounts

    with open(vdf_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # The top-level block is "users" { ... }
    for top_key, top_block in _iter_top_blocks(content):
        if top_key.lower() != "users":
            continue
        for steamid, block in _iter_top_blocks(top_block):
            if not (steamid.isdigit() and steamid.startswith("7656")):
                continue
            kv = _parse_vdf_block(block)
            ts_raw = kv.get("Timestamp", "0")
            try:
                ts = int(ts_raw)
                last_login = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
            except Exception:
                ts = 0
                last_login = "Неизвестно"

            accounts[steamid] = {
                "steamid":      steamid,
                "account_name": kv.get("AccountName", ""),
                "persona_name": kv.get("PersonaName", ""),
                "last_login":   last_login,
                "timestamp":    ts,
                "most_recent":  kv.get("MostRecent", "0") == "1",
                "avatar":       None,
                "ban_text":     "—",
                "ban_color":    "#7878a0",
            }

    return accounts


# ------------------------------------------------------------------
# Source 2: userdata/ folder
# ------------------------------------------------------------------

def _scan_userdata(steam_path: str) -> dict[str, dict]:
    """
    Every subfolder of userdata/ is named by accountID (lower 32 bits of SteamID64).
    Convert to SteamID64 and return minimal account dicts.
    """
    accounts = {}
    userdata_dir = os.path.join(steam_path, "userdata")
    if not os.path.isdir(userdata_dir):
        return accounts

    for entry in os.scandir(userdata_dir):
        if not entry.is_dir():
            continue
        try:
            account_id = int(entry.name)
            if account_id <= 0:
                continue
            steamid64 = str(account_id + STEAMID64_BASE)
        except ValueError:
            continue

        # Get folder mtime as approximate last-use timestamp
        try:
            ts = int(entry.stat().st_mtime)
            last_login = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
        except Exception:
            ts = 0
            last_login = "Неизвестно"

        accounts[steamid64] = {
            "steamid":      steamid64,
            "account_name": "",
            "persona_name": "",
            "last_login":   last_login,
            "timestamp":    ts,
            "most_recent":  False,
            "avatar":       None,
            "ban_text":     "—",
            "ban_color":    "#7878a0",
        }

    return accounts


# ------------------------------------------------------------------
# Source 3: Registry  HKCU\Software\Valve\Steam\Users
# ------------------------------------------------------------------

def _scan_registry() -> dict[str, dict]:
    accounts = {}
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Valve\Steam\Users"
        )
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                i += 1
                try:
                    account_id = int(subkey_name)
                    steamid64 = str(account_id + STEAMID64_BASE)
                    if steamid64 not in accounts:
                        accounts[steamid64] = {
                            "steamid":      steamid64,
                            "account_name": "",
                            "persona_name": "",
                            "last_login":   "Неизвестно",
                            "timestamp":    0,
                            "most_recent":  False,
                            "avatar":       None,
                            "ban_text":     "—",
                            "ban_color":    "#7878a0",
                        }
                except ValueError:
                    pass
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
    return accounts


# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------

def parse_all_accounts(steam_path: str) -> list[dict]:
    """
    Merges accounts from all sources. loginusers.vdf data takes priority
    (has account names + timestamps). userdata & registry fill in the rest.
    """
    from_vdf      = _parse_loginusers(steam_path)
    from_userdata = _scan_userdata(steam_path)
    from_registry = _scan_registry()

    merged: dict[str, dict] = {}

    # Start with userdata & registry (least info)
    for src in (from_userdata, from_registry):
        for sid, acc in src.items():
            if sid not in merged:
                merged[sid] = acc

    # loginusers.vdf overwrites with richer data
    for sid, acc in from_vdf.items():
        merged[sid] = acc

    accounts = list(merged.values())
    accounts.sort(key=lambda x: x["timestamp"], reverse=True)
    return accounts


# ------------------------------------------------------------------
# Public profile fetch (no API key)
# ------------------------------------------------------------------

def fetch_profile(steamid: str) -> dict:
    if not _REQUESTS_OK:
        return {}

    url = f"https://steamcommunity.com/profiles/{steamid}/?xml=1"
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except Exception:
        return {}

    result = {}

    persona = root.findtext("steamID")
    if persona:
        result["persona_name"] = persona

    avatar_url = root.findtext("avatarFull") or root.findtext("avatarMedium")
    if avatar_url:
        try:
            img = requests.get(avatar_url.strip(), timeout=6)
            img.raise_for_status()
            result["avatar_bytes"] = img.content
        except Exception:
            pass

    vac = root.findtext("vacBanned")
    result["vac_banned"] = vac == "1"

    trade_state = root.findtext("tradeBanState") or ""
    result["trade_ban"] = trade_state.lower() not in ("none", "")

    return result


def enrich_accounts(accounts: list[dict]) -> list[dict]:
    for acc in accounts:
        data = fetch_profile(acc["steamid"])

        if data.get("avatar_bytes"):
            acc["avatar"] = data["avatar_bytes"]

        if data.get("persona_name") and not acc["persona_name"]:
            acc["persona_name"] = data["persona_name"]

        vac   = data.get("vac_banned", False)
        trade = data.get("trade_ban", False)

        if vac and trade:
            acc["ban_text"]  = "VAC бан | Trade бан"
            acc["ban_color"] = "#e05252"
        elif vac:
            acc["ban_text"]  = "VAC бан"
            acc["ban_color"] = "#e05252"
        elif trade:
            acc["ban_text"]  = "Trade бан"
            acc["ban_color"] = "#e0a050"
        else:
            acc["ban_text"]  = "Не забанен"
            acc["ban_color"] = "#3dba6e"

    return accounts
