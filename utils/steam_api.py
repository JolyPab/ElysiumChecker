import requests
from datetime import datetime
import config


STEAM_API_BASE = "https://api.steampowered.com"


def _api_key() -> str:
    return config.get("steam_api_key", "")


def get_player_summaries(steam_ids: list[str]) -> dict:
    """
    Returns dict: steamid -> player summary dict.
    Fields: steamid, personaname, avatarfull, lastlogoff, profileurl, communityvisibilitystate
    """
    if not steam_ids:
        return {}
    key = _api_key()
    if not key:
        raise ValueError("Steam API ключ не задан")

    url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v0002/"
    ids_str = ",".join(steam_ids)
    resp = requests.get(url, params={"key": key, "steamids": ids_str}, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    players = data.get("response", {}).get("players", [])
    return {p["steamid"]: p for p in players}


def get_player_bans(steam_ids: list[str]) -> dict:
    """
    Returns dict: steamid -> ban info dict.
    Fields: VACBanned, NumberOfVACBans, DaysSinceLastBan, CommunityBanned, NumberOfGameBans
    """
    if not steam_ids:
        return {}
    key = _api_key()
    if not key:
        raise ValueError("Steam API ключ не задан")

    url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerBans/v1/"
    ids_str = ",".join(steam_ids)
    resp = requests.get(url, params={"key": key, "steamids": ids_str}, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    players = data.get("players", [])
    return {p["SteamId"]: p for p in players}


def download_avatar(url: str) -> bytes | None:
    """Downloads avatar image bytes, returns None on failure."""
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None


def format_last_seen(timestamp: int | None) -> str:
    if not timestamp:
        return "Неизвестно"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return "Неизвестно"


def format_vac_status(ban_info: dict) -> tuple[str, str]:
    """Returns (status_text, color)."""
    if not ban_info:
        return "Неизвестно", "#7878a0"

    vac = ban_info.get("VACBanned", False)
    game_bans = ban_info.get("NumberOfGameBans", 0)
    community = ban_info.get("CommunityBanned", False)

    parts = []
    if vac:
        n = ban_info.get("NumberOfVACBans", 1)
        days = ban_info.get("DaysSinceLastBan", 0)
        parts.append(f"VAC x{n} ({days}д. назад)")
    if game_bans:
        parts.append(f"Game Ban x{game_bans}")
    if community:
        parts.append("Community Ban")

    if parts:
        return " | ".join(parts), "#e05252"
    return "Не забанен", "#3dba6e"
