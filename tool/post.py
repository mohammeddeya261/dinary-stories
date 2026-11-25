import json, asyncio, pathlib, sys, shutil, html
from playwright.async_api import async_playwright

# Feed carousels (1080x1350) and simple stories (1080x1920) for Dinary weekly programs
# («فرصة الأسبوع», «حصاد الأسبوع», ...).
# usage: python3 tool/post.py <content.json> <out_dir> <prefix>
# Content format: see tool/post_example.json. Slide types: cover, item, list, story.
BASE = pathlib.Path(__file__).resolve().parent
F = str(BASE / "fonts" / "ibm-plex-sans-arabic")
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2]); PREFIX = sys.argv[3] if len(sys.argv) > 3 else "post"
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
NAVY, DEEP, LIME, SOFT, MUTED = "#200F8C", "#170A6B", "#D3D83E", "#DAD6F5", "#B9B3E6"
e = lambda s: html.escape(str(s or ""))

faces = "".join(
    f"@font-face{{font-family:P;font-weight:{w};src:url(file://{F}-{s}-{w}-normal.woff2)}}"
    for w in (400, 600, 700) for s in ("arabic", "latin"))

CSS = faces + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:P;direction:rtl;background:{NAVY};color:#fff;position:relative;overflow:hidden}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.05) 2px,transparent 2px);background-size:90px 90px}}
.corner{{position:absolute;left:0;top:0;width:240px;height:240px;background:{LIME};clip-path:polygon(0 0,100% 0,0 100%)}}
.top{{position:absolute;top:60px;right:70px;left:70px;display:flex;align-items:center;justify-content:space-between}}
.top .l{{display:flex;align-items:center;gap:18px}}
.pill{{background:{LIME};color:{NAVY};border-radius:999px;padding:8px 32px 12px;font-size:38px;font-weight:700}}
.num{{font-size:34px;font-weight:700;direction:ltr}}
.sub{{font-size:28px;font-weight:600;color:{SOFT}}}
.idx{{font-size:80px;font-weight:700;color:{LIME};line-height:1;direction:ltr}}
.main{{position:absolute;top:200px;bottom:120px;right:70px;left:70px;display:flex;flex-direction:column;gap:30px}}
.chip{{align-self:flex-start;background:rgba(255,255,255,.10);border:2px solid #4A3BB8;border-radius:999px;padding:10px 30px 14px;font-size:34px;font-weight:600}}
h1{{font-size:92px;font-weight:700;line-height:1.2}} h1 span,h2 span{{color:{LIME}}}
h2{{font-size:70px;font-weight:700;line-height:1.25}}
.big{{font-size:150px;font-weight:700;line-height:1;color:{LIME};direction:ltr;text-align:right}}
.bigl{{font-size:40px;font-weight:600;line-height:1.4}}
.name{{font-size:84px;font-weight:700;line-height:1.05;direction:ltr;text-align:right;font-family:'DejaVu Sans',sans-serif}}
.nsub{{font-size:44px;font-weight:700;line-height:1.35;color:{LIME}}}
.card{{background:#fff;border-radius:24px;padding:10px 34px;display:flex;flex-direction:column;color:{NAVY}}}
.r{{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:16px 0}}
.r+.r{{border-top:2px solid #E6E4F5}}
.r .k{{font-size:32px;font-weight:600;color:#5A5670;white-space:nowrap}}
.r .v{{font-size:33px;font-weight:700;text-align:left}}
.r .v.red{{font-size:36px;color:#C0392B}}
.li{{display:flex;gap:20px;align-items:baseline;padding:16px 0}} .li+.li{{border-top:2px solid #E6E4F5}}
.li b{{font-size:34px;direction:ltr}} .li span{{font-size:33px;font-weight:600}}
.box{{border:3px solid {LIME};border-radius:24px;padding:22px 30px;display:flex;flex-direction:column;gap:6px}}
.box b{{font-size:33px;color:{LIME}}} .box span{{font-size:33px;font-weight:500;line-height:1.5}}
.box.big2{{flex-direction:row;align-items:center;gap:24px;border-width:4px;border-radius:28px}}
.box.big2 b{{font-size:38px;color:#fff;display:block}} .box.big2 span{{font-size:30px;color:{MUTED}}}
.desc{{font-size:34px;line-height:1.55;color:{SOFT}}}
.kick{{font-size:30px;font-weight:600;color:{MUTED}}}
.src{{margin-top:auto;font-size:24px;color:{MUTED};line-height:1.5}}
.cta{{margin-top:auto;font-size:34px;font-weight:700}} .cta small{{display:block;font-size:28px;font-weight:400;color:{MUTED};margin-top:6px}}
.foot{{position:absolute;bottom:0;left:0;right:0;height:92px;background:{DEEP};border-top:6px solid {LIME};display:flex;align-items:center;justify-content:space-between;padding:0 70px}}
.foot.st{{bottom:300px;left:70px;right:70px;border-radius:20px}}
.logo{{display:flex;align-items:center;gap:16px}}
.mark{{width:40px;height:52px;background:#fff;border-radius:0 26px 26px 0;position:relative}}
.mark i{{position:absolute;left:14px;top:12px;width:13px;height:28px;background:{NAVY};border-radius:0 14px 14px 0}}
.logo span{{font-size:34px;font-weight:600;direction:ltr}}
.foot .when{{font-size:30px;font-weight:600;color:{SOFT}}}
.story .main{{top:300px;bottom:460px;right:90px;left:90px;justify-content:center;gap:44px}}
.story h1{{font-size:160px;line-height:1.05}} .story .desc{{font-size:52px;font-weight:600}}
"""
CLOCK = f'<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="{LIME}" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'

def top(s, show_idx):
    sub = f'<span class="sub">{e(data.get("date_line"))}</span>' if data.get("date_line") else ""
    num = f'<span class="num">{e(data.get("num"))}</span>' if data.get("num") else ""
    idx = f'<div class="idx">{e(s.get("n"))}</div>' if show_idx and s.get("n") else ""
    return f'<div class="top"><div class="l"><span class="pill">{e(data["program"])}</span>{num}{sub}</div>{idx}</div>'

def foot(story=False):
    return (f'<div class="foot{" st" if story else ""}"><div class="logo"><div class="mark"><i></i></div>'
            f'<span>dinary.iq</span></div><div class="when">{e(data.get("footer"))}</div></div>')

def title(a, b):
    return e(a) + (f'<br><span>{e(b)}</span>' if b else "")

def slide(s):
    t = s["type"]
    if t == "cover":
        big = (f'<div><div class="big">{e(s["big"])}</div><div class="bigl">{e(s.get("big_label"))}</div></div>'
               if s.get("big") else "")
        lst = ("".join(f'<div class="li"><b>{i+1:02d}</b><span>{e(x)}</span></div>' for i, x in enumerate(s.get("items", []))))
        lst = f'<div class="card">{lst}</div>' if s.get("items") else ""
        box = (f'<div class="box big2">{CLOCK}<div><b>{e(s["box_title"])}</b><span>{e(s.get("box_sub"))}</span></div></div>'
               if s.get("box_title") else "")
        chip = f'<div class="chip">{e(s["chip"])}</div>' if s.get("chip") else ""
        inner = f'{chip}<h1>{title(s["title"], s.get("title2"))}</h1>{big}{lst}{box}<div class="cta">{e(s.get("cta"))}</div>'
        return True, False, inner
    if t == "item":
        rows = "".join(f'<div class="r"><div class="k">{e(k)}</div><div class="v{" red" if i == len(s["rows"]) - 1 and s.get("last_red") else ""}">{e(v)}</div></div>'
                       for i, (k, v) in enumerate(s.get("rows", [])))
        head = (f'<div><div class="name">{e(s["name"])}</div><div class="nsub">{e(s.get("sub"))}</div></div>' if s.get("name")
                else f'<div class="kick">{e(s.get("kicker"))}</div><h2>{e(s["title"])}</h2>')
        big = f'<div><div class="big">{e(s["big"])}</div><div class="bigl">{e(s.get("big_label"))}</div></div>' if s.get("big") else ""
        desc = f'<div class="desc">{e(s["desc"])}</div>' if s.get("desc") else ""
        card = f'<div class="card">{rows}</div>' if rows else ""
        box = f'<div class="box"><b>{e(s.get("why_title", "ليش يهمك؟"))}</b><span>{e(s["why"])}</span></div>' if s.get("why") else ""
        return False, True, f'{head}{big}{desc}{card}{box}<div class="src">{e(s.get("source"))}</div>'
    if t == "list":
        lst = "".join(f'<div class="li"><b>{i+1:02d}</b><span>{e(x)}</span></div>' for i, x in enumerate(s["items"]))
        box = f'<div class="box"><b>{e(s.get("note_title", "انتبه"))}</b><span>{e(s["note"])}</span></div>' if s.get("note") else ""
        return True, False, (f'<h2>{title(s["title"], s.get("title2"))}</h2><div class="card">{lst}</div>{box}'
                             f'<div class="cta">{e(s.get("cta"))}<small>{e(s.get("cta_sub"))}</small></div>')
    if t == "story":
        chip = f'<div class="chip">{e(s["chip"])}</div>' if s.get("chip") else ""
        box = (f'<div class="box big2"><div><b>{e(s["box_title"])}</b><span>{e(s.get("box_sub"))}</span></div></div>'
               if s.get("box_title") else "")
        return True, False, f'{chip}<h1>{title(s["title"], s.get("title2"))}</h1><div class="desc">{e(s.get("desc"))}</div>{box}'
    raise SystemExit(f"unknown slide type {t}")

def page(s):
    story = s["type"] == "story"
    corner, show_idx, inner = slide(s)
    h = 1920 if story else 1350
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{CSS}'
            f'body{{width:1080px;height:{h}px}}</style></head><body class="{"story" if story else ""}">'
            f'<div class="grid"></div>{"<div class=corner></div>" if corner else ""}'
            f'{"" if story else top(s, show_idx)}<div class="main">{inner}</div>{foot(story)}</body></html>')

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME) if CHROME else await p.chromium.launch()
        for i, s in enumerate(data["slides"]):
            h = 1920 if s["type"] == "story" else 1350
            pg = await b.new_page(viewport={"width": 1080, "height": h})
            await pg.set_content(page(s)); await pg.wait_for_timeout(400)
            over = await pg.evaluate("(()=>{const m=document.querySelector('.main');return m.scrollHeight>m.clientHeight+2})()")
            f = OUT / f"{PREFIX}_{i}.jpg"
            await pg.screenshot(path=str(f), type="jpeg", quality=92)
            print(f, "OVERFLOW" if over else "ok")
            await pg.close()
        await b.close()

asyncio.run(main())
