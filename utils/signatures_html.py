"""
Generates a local HTML file with Everything search queries and opens it in the browser.
"""
import os
import base64
import tempfile
import webbrowser

# ── Query sets ────────────────────────────────────────────────────────

SECTIONS = [
    {
        "title":    "Everything",
        "subtitle": "Поиск файлов по размеру в Everything",
        "query":    "size:20051kb | size:15110kb | size:13030kb | size:13485kb | size:17487kb | size:4311kb | size:16809kb | size:15090kb",
    },
    {
        "title":    "Everything",
        "subtitle": "Поиск по названиям известных читов",
        "query":    "exloader | com.swiftsoft | xone | interium | skinchanger | extrimhack | nix | memesense | mvploader | sharkhack | exhack | neverkernel | vredux | mason | predator | aquila | luno | fecurity | cartel | aimstar | tkazer | naim | pellix | pussycat | axios | onemacro | softhub | proext | sapphire | interwebz | plague | vapehook | smurfwrecker | iniuria | yeahnot | legendware | hauntedproject | phoenixhack | onebyteradar | reborn | onebyte | osiris | ev0lve | ghostware | dexterion | basicmultihack | pudra | iCheat | sneakys | krazyhack | muhprime | drcheats | rootcheat | aeonix | zedt.pw | devcore | legifard | katebot | imxnoobx | w1nner | ekknod | neoxahack | warware | weave | aimmy | paradise | xenon | easysp | en1gma | Injector | .ahk | macros | bhop | bunnyhop | espd2x | avira | pphud | primordial | nonagon | legit | hvh | aimbot | s1mple | semirage | cheat | cs2.glow | invision | undetek | spurdo | webradar | valthrun",
    },
    {
        "title":    "Everything",
        "subtitle": "Поиск остаточных файлов читов",
        "query":    "token.ms | schinese.bin | russian.bin | esp-icons.ttf | message-bus.bin | nl.log | nl_cs2.log",
    },
    {
        "title":    "Everything",
        "subtitle": "Поиск исключительно: midnight, xone, nixware, spurdo",
        "query":    "size:10mb-20mb ext:exe utf8content:\"xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>\"",
    },
    {
        "title":    "SystemInformer",
        "subtitle": "Только для процесса csrss.exe",
        "query":    r"^(([a-zA-Z]{1}:|\\)(\\[^\\/<>:\|\*\?\"]+)+\.[^\\/<>:\|]{3,4})",
    },
    {
        "title":    "SystemInformer",
        "subtitle": "Поиск посещений сайтов с читами",
        "query":    "doomxtf.com|axios-macro.com|midnight.im|xone.fun|blast.hk|yougame.biz|jestkii|wh-satano|cheatcsgo|interium|r8cheats|ezcheats|exloader|cs-elect.ru|extrimhack|neverlose.cc|gamesense|legendware|nixware|phoenix-hack|rf-cheats|anyx.gg|hackvshack.net|ezyhack|unknowncheats|cheater.ninja|insanitycheats.com|cheater.fun|100cheats.ru|undetek.com|cs-elect.ru|cheater.world|zelenka.guru/tags/cs2-cheat|procheats|hells-hack.com|clickhack.ru|procheat.pro|cheatermad.com|420cheats.com|cs2-cheat|wh-satano.ru|up-game.pro|millex.xyz|boohack.ru|procheat.pro|elitehacks.ru|cheatcsgo.ru|box-cheat.ru|novamacro|predator.systems|mvploader|securecheats|darkaim|invision.gg|elitepvpers.com|privatecheatz|cosmocheats|skycheats.com|rockpapershotgun.com|en1gma.tech|lunocs2.ru|abyss.gg|ezcs.ru|kitchenhack.ru|ezyhack.ru|extrimhack.ru|dhjcheats.com|aimcop.ru|novamacro.xyz|promacro.ru|promacro.store|botmek.ru|topmacro.ru|ggmacro.ru|aimstar|myhacks.store|interium.ooo|nixware.cc|arayas-cheats.com|x-cheats.com|r8cheats.guru|gamebreaker.ru|cheatside.ru|shadowcheat.pro|h4ck.shop|select-place.ru|oplata.info|Spurdo.me|Chieftain",
    },
]


def _build_html() -> str:
    logo_uri = _logo_data_uri()
    cards_html = ""
    # Group cards by title for section labels
    current_group = None
    for i, sec in enumerate(SECTIONS):
        group = sec["title"]

        # Section label when group changes
        if group != current_group:
            current_group = group
            if group == "Everything":
                icon_class = "icon-everything"
                emoji      = "🔍"
                title_color = "#e91e8c"
            else:
                icon_class = "icon-systeminformer"
                emoji      = "⚙️"
                title_color = "#c084fc"
            cards_html += f'<div class="section-label"><span>{group}</span></div>\n'

        cards_html += f"""
        <div class="card">
          <div class="card-header">
            <div class="card-left">
              <div class="card-icon {icon_class}">{emoji}</div>
              <div>
                <div class="card-title" style="color:{title_color}">{sec['title']}</div>
                <div class="card-subtitle">{sec['subtitle']}</div>
              </div>
            </div>
            <button class="copy-btn" onclick="copyText('q{i}')">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              Копировать
            </button>
          </div>
          <div class="query-box" id="q{i}">{sec['query']}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>ElysiumChecker — Сигнатуры</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:        #0a0414;
    --bg2:       #110820;
    --card:      #15092a;
    --border:    #2a0f4a;
    --accent1:   #e91e8c;
    --accent2:   #7b2fb5;
    --text:      #f0e4f8;
    --muted:     #a070c0;
    --dim:       #4a2870;
    --green:     #2ec27e;
    --mono:      'Consolas', 'Courier New', monospace;
  }}

  html {{ scroll-behavior: smooth; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', 'Segoe UI', sans-serif;
    min-height: 100vh;
    padding-bottom: 60px;
  }}

  /* ── Top bar ── */
  .topbar {{
    background: linear-gradient(135deg, #0d0520 0%, #180535 100%);
    border-bottom: 1px solid var(--border);
    padding: 22px 48px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(12px);
  }}
  .topbar-logo-img {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
  }}
  .topbar-logo-fallback {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent2), var(--accent1));
    flex-shrink: 0;
  }}
  .topbar-text h1 {{
    font-size: 17px;
    font-weight: 700;
    background: linear-gradient(90deg, #c084fc, var(--accent1));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
  }}
  .topbar-text p {{
    font-size: 12px;
    color: var(--dim);
    margin-top: 1px;
  }}

  /* ── Layout ── */
  .page {{
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 24px 0;
  }}

  .section-label {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 36px 0 14px;
  }}
  .section-label span {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--muted);
  }}
  .section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }}

  /* ── Card ── */
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    margin-bottom: 14px;
    overflow: hidden;
    transition: border-color .2s, box-shadow .2s;
  }}
  .card:hover {{
    border-color: #4a1880;
    box-shadow: 0 0 24px rgba(123,47,181,.15);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
  }}

  .card-left {{
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }}

  .card-icon {{
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }}
  .icon-everything {{
    background: rgba(233,30,140,.15);
    border: 1px solid rgba(233,30,140,.25);
  }}
  .icon-systeminformer {{
    background: rgba(123,47,181,.2);
    border: 1px solid rgba(123,47,181,.35);
  }}

  .card-title {{
    font-size: 15px;
    font-weight: 700;
  }}
  .card-subtitle {{
    font-size: 12px;
    color: var(--muted);
    margin-top: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .copy-btn {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    background: linear-gradient(90deg, var(--accent2), var(--accent1));
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    transition: opacity .15s, transform .1s;
  }}
  .copy-btn:hover  {{ opacity: .88; transform: translateY(-1px); }}
  .copy-btn:active {{ transform: translateY(0); }}
  .copy-btn.copied {{
    background: var(--green);
  }}

  /* ── Query box ── */
  .query-box {{
    padding: 16px 20px;
    font-family: var(--mono);
    font-size: 12.5px;
    line-height: 1.8;
    color: #c8a8e8;
    word-break: break-all;
    cursor: text;
    user-select: all;
  }}

  /* ── Footer ── */
  footer {{
    margin-top: 52px;
    text-align: center;
    padding: 20px;
    border-top: 1px solid var(--border);
    color: var(--dim);
    font-size: 12px;
  }}
  footer span {{
    background: linear-gradient(90deg, var(--accent2), var(--accent1));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600;
  }}
</style>
</head>
<body>

<div class="topbar">
  {'<img src="' + logo_uri + '" class="topbar-logo-img" alt="logo">' if logo_uri else '<div class="topbar-logo-fallback"></div>'}
  <div class="topbar-text">
    <h1>ElysiumChecker</h1>
    <p>База сигнатур для проверки на читы</p>
  </div>
</div>

<div class="page">
  {cards_html}
</div>

<footer>
  Сделано для &nbsp;<span>Elysium CS2</span>&nbsp; · ElysiumChecker
</footer>

<script>
function copyText(id) {{
  const el  = document.getElementById(id);
  const btn = el.closest('.card').querySelector('.copy-btn');
  navigator.clipboard.writeText(el.innerText).then(() => {{
    const orig = btn.innerHTML;
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Скопировано';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.innerHTML = orig; btn.classList.remove('copied'); }}, 1800);
  }});
}}
</script>
</body>
</html>"""


def _logo_data_uri() -> str:
    """Returns a base64 data URI for logo.gif or logo.png, or empty string."""
    from utils.paths import base_dir
    base = base_dir()
    for fname, mime in [("logo.gif", "image/gif"), ("logo.png", "image/png")]:
        path = os.path.join(base, fname)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{b64}"
    return ""


def open_signatures():
    """Generate HTML to a temp file and open in default browser."""
    html = _build_html()
    tmp = os.path.join(tempfile.gettempdir(), "elysium_signatures.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file:///{tmp.replace(os.sep, '/')}")
