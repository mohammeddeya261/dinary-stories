import json, asyncio, pathlib, sys, shutil
from playwright.async_api import async_playwright

# usage: python3 tool/make.py <content.json> <out_dir> [prefix]
BASE = pathlib.Path(__file__).resolve().parent
F = str(BASE / "fonts" / "ibm-plex-sans-arabic")
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2]); PREFIX = sys.argv[3] if len(sys.argv) > 3 else "story"
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")

faces = "".join(
    f"@font-face{{font-family:P;font-weight:{w};src:url(file://{F}-{s}-{w}-normal.woff2)}}"
    for w in (400, 600, 700) for s in ("arabic", "latin"))

CSS = faces + """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;font-family:P;direction:rtl;color:#fff;background:#150873;position:relative;overflow:hidden}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 50% 46%,rgba(80,60,230,.85) 0%,rgba(31,14,139,.55) 38%,rgba(16,6,90,.94) 78%)}
.foot-glow{position:absolute;left:0;right:0;bottom:0;height:560px;background:linear-gradient(to top,rgba(211,216,62,.10),rgba(211,216,62,0))}
.corner{position:absolute;top:0;left:0;width:320px;height:320px;background:#D3D83E;clip-path:polygon(0 0,100% 0,0 100%)}
.logo{position:absolute;top:200px;right:80px;display:flex;align-items:center;gap:16px}
.mark{width:52px;height:66px;background:#fff;border-radius:0 33px 33px 0;position:relative}
.mark i{position:absolute;left:18px;top:15px;width:17px;height:36px;background:#1F0E8B;border-radius:0 18px 18px 0}
.logo b{font-size:28px;font-weight:700;letter-spacing:9px;direction:ltr}
.wrap{position:absolute;top:330px;right:80px;left:80px;display:flex;flex-direction:column;gap:32px}
.row{display:flex;align-items:center;gap:18px}
.pill{background:#D3D83E;color:#1F0E8B;font-size:34px;font-weight:700;padding:8px 32px;border-radius:999px}
.date{font-size:32px;font-weight:600;color:rgba(255,255,255,.88)}
.kicker{font-size:34px;font-weight:600;color:#D3D83E}
h1{font-size:82px;font-weight:700;line-height:1.25;text-shadow:0 10px 36px rgba(0,0,0,.4)}
.card{background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.16);border-radius:40px;padding:40px 44px 44px}
.card .big{font-size:160px;font-weight:700;line-height:1.05;color:#D3D83E;direction:ltr;text-align:right;letter-spacing:-3px;text-shadow:0 14px 44px rgba(0,0,0,.35)}
.card .big.word{direction:rtl;font-size:150px;letter-spacing:0}
.card .lbl{font-size:36px;font-weight:600;margin-top:8px}
.note{background:#D3D83E;color:#1F0E8B;border-radius:32px;padding:30px 36px}
.note b{display:block;font-size:32px;font-weight:700}
.note span{font-size:32px;font-weight:600;line-height:1.55}
.body{font-size:38px;line-height:1.6;color:rgba(255,255,255,.92)}
.foot{position:absolute;bottom:210px;right:80px;left:80px;display:flex;justify-content:space-between;align-items:center}
.foot .src{font-size:27px;color:rgba(255,255,255,.85)}
.foot .h{font-size:28px;font-weight:600;direction:ltr}
.cover h1{font-size:150px;line-height:1.15}
.cover h1 em{font-style:normal;color:#D3D83E}
.list{display:flex;flex-direction:column;gap:22px;margin-top:20px}
.item{background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.16);border-radius:28px;padding:24px 30px;display:flex;align-items:center;gap:26px;font-size:40px;font-weight:600}
.item i{font-style:normal;width:64px;height:64px;border-radius:50%;background:#D3D83E;color:#1F0E8B;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0}
"""

def frame(inner, src=""):
    return f'''<body><div class="glow"></div><div class="foot-glow"></div><div class="corner"></div>
<div class="logo"><div class="mark"><i></i></div><b>DINARY</b></div>
<div class="wrap">{inner}</div>
<div class="foot"><div class="src">{src}</div><div class="h">{data["handle"]}</div></div></body>'''

def cover():
    items = "".join(f'<div class="item"><i>{i+1}</i>{n["short"]}</div>' for i, n in enumerate(data["news"]))
    return frame(f'''<div class="row"><div class="pill">اقتصاد اليوم</div><div class="date">{data["date"]}</div></div>
<div class="cover"><h1>أهم أخبار<br><em>الاقتصاد</em> اليوم</h1></div><div class="list">{items}</div>''')

def story(i, n):
    word = " word" if not any(c.isdigit() for c in n["stat"]) else ""
    note = f'<div class="note"><b>زاوية اقتصادية</b><span>{n["angle"]}</span></div>' if n.get("angle") else ""
    return frame(f'''<div class="row"><div class="pill">{data.get("pill","اقتصاد اليوم")}</div><div class="date">{data["date"]}</div></div>
<div class="kicker">{(str(i+1)+"/"+str(len(data["news"]))+" · ") if len(data["news"])>1 else ""}{n["tag"]}</div><h1>{n["title"]}</h1>
<div class="card"><div class="big{word}">{n["stat"]}</div><div class="lbl">{n["stat_label"]}</div></div>
<div class="body">{n["body"]}</div>{note}''', "المصدر: " + n["source"])

async def main():
    out = OUT; out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path("/tmp/dinary_html"); tmp.mkdir(exist_ok=True)
    pages = ([cover()] if data.get("cover", True) else []) + [story(i, n) for i, n in enumerate(data["news"])]
    async with async_playwright() as p:
        b = await (p.chromium.launch(executable_path=CHROME) if CHROME else p.chromium.launch())
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for k, body in enumerate(pages):
            f = tmp / f"{k:02d}.html"
            f.write_text(f"<!DOCTYPE html><html lang=ar><head><meta charset=utf-8><style>{CSS}</style></head>{body}</html>")
            await pg.goto(f"file://{f}"); await pg.evaluate("document.fonts.ready")
            png = tmp / f"{k}.png"; await pg.screenshot(path=str(png))
            from PIL import Image; Image.open(png).convert("RGB").save(out / f"{PREFIX}_{k}.jpg", quality=92)
        await b.close()

asyncio.run(main())
