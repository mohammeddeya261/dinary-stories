import json, asyncio, pathlib, sys, shutil, datetime
from playwright.async_api import async_playwright

# usage: python3 tool/make.py <content.json> <out_dir> [prefix]
# Each news item may set "layout": navy | lime | light | split | quote.
# Without it, layouts rotate automatically so no two neighbouring stories look alike.
BASE = pathlib.Path(__file__).resolve().parent
F = str(BASE / "fonts" / "ibm-plex-sans-arabic")
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2]); PREFIX = sys.argv[3] if len(sys.argv) > 3 else "story"
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
ROTATION = ["navy", "lime", "split", "light"]
NAVY, INK, LIME = "#150873", "#1F0E8B", "#D3D83E"

import base64
def furl(path):
    return "data:font/woff2;base64," + base64.b64encode(open(path, "rb").read()).decode()
RANGES = {"arabic": "U+0600-06FF,U+0750-077F,U+0870-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC", "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"}
faces = "".join(
    f"@font-face{{font-family:P;font-weight:{w};src:url({furl(F + f'-{s}-{w}-normal.woff2')});unicode-range:{RANGES[s]}}}"
    for w in (400, 600, 700) for s in ("arabic", "latin"))

CSS = faces + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;font-family:P;direction:rtl;position:relative;overflow:hidden;--fg:#fff;--acc:{LIME};--mark:#fff;--markin:{INK};color:var(--fg)}}
.logo{{position:absolute;top:200px;right:80px;display:flex;align-items:center;gap:16px;z-index:3}}
.mark{{width:52px;height:66px;background:var(--mark);border-radius:0 33px 33px 0;position:relative}}
.mark i{{position:absolute;left:18px;top:15px;width:17px;height:36px;background:var(--markin);border-radius:0 18px 18px 0}}
.logo b{{font-size:28px;font-weight:700;letter-spacing:9px;direction:ltr;color:var(--fg)}}
.wrap{{position:absolute;top:330px;right:80px;left:80px;display:flex;flex-direction:column;gap:32px;z-index:2}}
.row{{display:flex;align-items:center;gap:18px}}
.pill{{background:{LIME};color:{INK};font-size:34px;font-weight:700;padding:8px 32px;border-radius:999px}}
.date{{font-size:32px;font-weight:600;opacity:.88}}
.kicker{{font-size:34px;font-weight:600;color:var(--acc)}}
h1{{font-size:82px;font-weight:700;line-height:1.25}}
.big{{font-weight:700;line-height:1.05;direction:ltr;text-align:right;letter-spacing:-3px}}
.big.word{{direction:rtl;letter-spacing:0}}
.lbl{{font-size:36px;font-weight:600;margin-top:8px}}
.body{{font-size:38px;line-height:1.6}}
.note{{border-radius:32px;padding:30px 36px}}
.note b{{display:block;font-size:32px;font-weight:700}}
.note span{{font-size:32px;font-weight:600;line-height:1.55}}
.foot{{position:absolute;bottom:210px;right:80px;left:80px;display:flex;justify-content:space-between;align-items:center;z-index:3}}
.foot .src{{font-size:27px;opacity:.85}}
.foot .h{{font-size:28px;font-weight:600;direction:ltr}}

/* navy */
.navy{{background:{NAVY}}}
.navy .glow{{position:absolute;inset:0;background:radial-gradient(circle at 50% 46%,rgba(80,60,230,.85) 0%,rgba(31,14,139,.55) 38%,rgba(16,6,90,.94) 78%)}}
.navy .corner{{position:absolute;top:0;left:0;width:320px;height:320px;background:{LIME};clip-path:polygon(0 0,100% 0,0 100%)}}
.navy h1{{text-shadow:0 10px 36px rgba(0,0,0,.4)}}
.navy .card{{background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.16);border-radius:40px;padding:40px 44px 44px}}
.navy .big{{font-size:160px;color:{LIME}}} .navy .big.word{{font-size:150px}}
.navy .note{{background:{LIME};color:{INK}}}

/* lime */
.lime{{background:{LIME};--fg:{INK};--acc:{INK};--mark:{INK};--markin:{LIME}}}
.lime .corner{{position:absolute;bottom:0;right:0;width:420px;height:420px;background:{INK};clip-path:polygon(100% 0,100% 100%,0 100%);opacity:.12}}
.lime .pill{{background:{INK};color:{LIME}}}
.lime .kicker{{opacity:.75}}
.lime .big{{font-size:230px;color:{INK};letter-spacing:-6px;margin-top:10px}} .lime .big.word{{font-size:190px}}
.lime .lbl{{font-size:38px;border-top:6px solid {INK};padding-top:18px;margin-top:0}}
.lime .note{{background:{INK};color:#fff}} .lime .note b{{color:{LIME}}}

/* light */
.light{{background:#F4F3FB;--fg:{INK};--acc:#5a4bd8;--mark:{INK};--markin:#F4F3FB}}
.light .corner{{position:absolute;top:0;left:0;right:0;height:22px;background:{LIME}}}
.light .blob{{position:absolute;left:0;top:900px;width:480px;height:700px;border-radius:0 350px 350px 0;background:{LIME};opacity:.35}}
.light .card{{background:{INK};color:#fff;border-radius:40px;padding:40px 44px 44px;box-shadow:0 30px 60px rgba(31,14,139,.25)}}
.light .big{{font-size:160px;color:{LIME}}} .light .big.word{{font-size:150px}}
.light .body{{color:#2a2160}}
.light .note{{background:#fff;border:3px solid {INK};color:{INK}}}

/* split */
.split{{background:#fff;--fg:#fff}}
.split .top{{position:absolute;left:0;right:0;top:0;height:1060px;background:{NAVY};clip-path:polygon(0 0,100% 0,100% 92%,0 100%)}}
.split .wrap{{gap:30px}}
.split .card{{background:{LIME};color:{INK};border-radius:40px;padding:36px 44px 40px;margin-top:30px;box-shadow:0 26px 50px rgba(21,8,115,.35)}}
.split .big{{font-size:170px;color:{INK}}} .split .big.word{{font-size:150px}}
.split .body{{color:{INK}}}
.split .note{{background:#EEECFA;color:{INK}}}
.split .foot{{color:{INK}}}

/* quote */
.quote{{background:{INK}}}
.quote .qm{{position:absolute;right:40px;top:300px;font-size:700px;line-height:1;color:{LIME};opacity:.14;font-weight:700}}
.quote .say{{font-size:70px;font-weight:700;line-height:1.4;border-right:12px solid {LIME};padding-right:40px;margin-top:20px}}
.quote .who{{font-size:38px;font-weight:600;color:{LIME}}}
.quote .tagword{{display:inline-block;background:rgba(211,216,62,.15);border:2px solid {LIME};color:{LIME};font-size:44px;font-weight:700;padding:10px 34px;border-radius:999px;align-self:flex-start}}
.quote .note{{background:{LIME};color:{INK}}}

/* covers */
.cover h1{{font-size:150px;line-height:1.15}}
.cover h1 em{{font-style:normal;color:var(--acc)}}
.list{{display:flex;flex-direction:column;gap:22px;margin-top:20px}}
.item{{border-radius:28px;padding:24px 30px;display:flex;align-items:center;gap:26px;font-size:40px;font-weight:600}}
.navy .item{{background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.16)}}
.lime .item{{background:rgba(31,14,139,.08);border:2px solid rgba(31,14,139,.25)}}
.item i{{font-style:normal;width:64px;height:64px;border-radius:50%;background:{LIME};color:{INK};display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0}}
.lime .item i{{background:{INK};color:{LIME}}}
"""

DECOR = {
    "navy": '<div class="glow"></div><div class="corner"></div>',
    "lime": '<div class="corner"></div>',
    "light": '<div class="corner"></div><div class="blob"></div>',
    "split": '<div class="top"></div>',
    "quote": '<div class="qm">”</div>',
}

def frame(theme, inner, src=""):
    return f'''<body class="{theme}">{DECOR[theme]}
<div class="logo"><div class="mark"><i></i></div><b>DINARY</b></div>
<div class="wrap">{inner}</div>
<div class="foot"><div class="src">{src}</div><div class="h">{data["handle"]}</div></div></body>'''

def head(i, n):
    count = f"{i+1}/{len(data['news'])} · " if len(data["news"]) > 1 else ""
    return (f'<div class="row"><div class="pill">{data.get("pill","اقتصاد اليوم")}</div><div class="date">{data["date"]}</div></div>'
            f'<div class="kicker">{count}{n["tag"]}</div>')

def note(n):
    return f'<div class="note"><b>زاوية اقتصادية</b><span>{n["angle"]}</span></div>' if n.get("angle") else ""

def stat(n):
    word = "" if any(c.isdigit() for c in n["stat"]) else " word"
    return f'<div class="big{word}">{n["stat"]}</div><div class="lbl">{n["stat_label"]}</div>'

def story(i, n, theme):
    src = "المصدر: " + n["source"]
    if theme == "quote":
        say = n.get("quote") or n["title"]
        return frame(theme, f'''{head(i,n)}<div class="say">{say}</div><div class="who">— {n.get("speaker", n["source"])}</div>
<div class="tagword">{n["stat"]}</div><div class="body">{n["body"]}</div>{note(n)}''', src)
    if theme == "lime":
        return frame(theme, f'{head(i,n)}<h1>{n["title"]}</h1><div>{stat(n)}</div><div class="body">{n["body"]}</div>{note(n)}', src)
    if theme == "split":
        return frame(theme, f'{head(i,n)}<h1>{n["title"]}</h1><div class="card">{stat(n)}</div><div class="body">{n["body"]}</div>{note(n)}', src)
    return frame(theme, f'{head(i,n)}<h1>{n["title"]}</h1><div class="card">{stat(n)}</div><div class="body">{n["body"]}</div>{note(n)}', src)

def cover():
    theme = data.get("cover_layout") or ("navy" if datetime.date.today().toordinal() % 2 else "lime")
    items = "".join(f'<div class="item"><i>{i+1}</i>{n["short"]}</div>' for i, n in enumerate(data["news"]))
    return frame(theme, f'''<div class="row"><div class="pill">اقتصاد اليوم</div><div class="date">{data["date"]}</div></div>
<div class="cover"><h1>أهم أخبار<br><em>الاقتصاد</em> اليوم</h1></div><div class="list">{items}</div>''')

def themes():
    start = datetime.date.today().toordinal() % len(ROTATION)
    out, prev = [], None
    for i, n in enumerate(data["news"]):
        t = n.get("layout") or ROTATION[(start + i) % len(ROTATION)]
        if t == prev and not n.get("layout"):
            t = ROTATION[(ROTATION.index(t) + 1) % len(ROTATION)]
        out.append(t); prev = t
    return out

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path("/tmp/dinary_html"); tmp.mkdir(exist_ok=True)
    pages = ([cover()] if data.get("cover", True) else []) + [story(i, n, t) for i, (n, t) in enumerate(zip(data["news"], themes()))]
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=CHROME) if CHROME else p.chromium.launch())
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for k, body in enumerate(pages):
            f = tmp / f"{k:02d}.html"
            f.write_text(f"<!DOCTYPE html><html lang=ar><head><meta charset=utf-8><style>{CSS}</style></head>{body}</html>")
            await pg.goto(f"file://{f}"); await pg.evaluate("document.fonts.ready")
            png = tmp / f"{k}.png"; await pg.screenshot(path=str(png))
            from PIL import Image; Image.open(png).convert("RGB").save(OUT / f"{PREFIX}_{k}.jpg", quality=92)
        await b.close()

asyncio.run(main())
