import asyncio, pathlib, sys, shutil, subprocess, base64, random, json
from playwright.async_api import async_playwright

# Instagram stories (1080x1920) for «السوق العقاري», in Dinary identity: a still JPEG and a short
# animated MP4 of the same design. Content stays inside the story safe zone (y 260–1580).
# usage: python3 tool/story_aqari.py <story.json> <out_prefix>
# story.json: {"kind":"teaser"|"launch", "chip", "title", "title2", "sub", "ask", "ask_hint",
#              "cover" (image path, launch only), "cta", "foot", "seconds"}
BASE = pathlib.Path(__file__).resolve().parent
FD = BASE / "fonts"
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2])
FPS, SEC = 30, float(cfg.get("seconds", 6))
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
AR = "U+0600-06FF,U+0750-077F,U+0870-08FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFC"
LA = "U+0000-00FF,U+2000-206F,U+20AC,U+2212"
def b64(p, mime): return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
faces = "".join(f"@font-face{{font-family:P;font-weight:{w};src:url({b64(FD / f'ibm-plex-sans-arabic-{s}-{w}-normal.woff2', 'font/woff2')});unicode-range:{r}}}"
                for w in (400, 600, 700) for s, r in (("arabic", AR), ("latin", LA)))
NAVY, LIME, DEEP = "#200F8C", "#D3D83E", "#120565"
ROOF = ("data:image/svg+xml," + __import__("urllib.parse").parse.quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="70"><path d="M10 50 L40 22 L70 50 M70 50 L100 22 L130 50" fill="none" stroke="{LIME}" stroke-opacity=".07" stroke-width="3"/></svg>'))

random.seed(5)
GROUND = 1920
blds = [(x, GROUND - h, w, h) for x, w, h in [(-10,160,250),(150,130,330),(280,180,210),(460,140,380),(600,170,280),(770,150,230),(920,170,310)]]
city = []
for i, (x, y, w, h) in enumerate(blds):
    wins = "".join(f'<rect class="w" data-t="{random.uniform(.6, 3.2):.2f}" x="{wx}" y="{wy}" width="18" height="26" rx="2"/>'
                   for wy in range(y + 34, y + h - 30, 52) for wx in range(x + 24, x + w - 34, 38))
    roof = f'<path d="M{x+6} {y+18} L{x+w/2} {y-22} L{x+w-6} {y+18}" fill="none" stroke="{LIME}" stroke-width="3"/>' if i % 2 else ""
    city.append(f'<g class="b" data-i="{i}"><rect x="{x+6}" y="{y+18 if i%2 else y}" width="{w-12}" height="{h}" fill="#1A0B7A" stroke="{LIME}" stroke-width="3"/>{roof}{wins}</g>')
cx, cy = 530, GROUND - 380
crane = (f'<g><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-140}" stroke="{LIME}" stroke-width="5"/>'
         f'<g id="arm" style="transform-origin:{cx}px {cy-140}px"><line x1="{cx-60}" y1="{cy-140}" x2="{cx+220}" y2="{cy-140}" stroke="{LIME}" stroke-width="5"/>'
         f'<line x1="{cx+170}" y1="{cy-140}" x2="{cx+170}" y2="{cy-60}" stroke="#fff" stroke-width="2"/><rect x="{cx+150}" y="{cy-60}" width="40" height="26" fill="{LIME}"/></g></g>')
stars = "".join(f'<circle class="s" data-p="{random.uniform(0,6.28):.2f}" cx="{random.randint(20,1060)}" cy="{random.randint(40,1300)}" r="{random.choice([1.5,2,2.5])}" fill="#fff"/>' for _ in range(60))
SKY = (f'<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">{stars}'
       f'<circle cx="930" cy="1330" r="50" fill="#fff" opacity=".9"/><circle cx="950" cy="1318" r="44" fill="#2A16A8"/>'
       f'{"".join(city)}</svg>')

teaser = cfg["kind"] == "teaser"
if teaser:
    body = f"""
<div class="chip" id="a1"><span class="dot"></span>{cfg['chip']}</div>
<h1 id="a2">{cfg['title']}<br><span>{cfg['title2']}</span></h1>
<div class="sub" id="a3">{cfg['sub']}</div>
<div class="ask" id="a4"><div class="q">{cfg['ask']}</div><div class="hint">{cfg['ask_hint']}</div></div>"""
else:
    body = f"""
<div class="chip" id="a1"><span class="dot"></span>{cfg['chip']}</div>
<h2 id="a2">{cfg['title']}<br><span>{cfg['title2']}</span></h2>
<div class="cover" id="a3"><img src="{b64(cfg['cover'], 'image/jpeg')}"></div>
<div class="go" id="a4">{cfg['cta']}</div>"""

HTML = f"""<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:P;color:#fff;
background:radial-gradient(circle at 50% 32%,#3A27C4 0%,{NAVY} 48%,{DEEP} 100%)}}
.pat{{position:absolute;inset:0;background-image:url("{ROOF}");background-size:120px 70px}}
.corner{{position:absolute;left:0;top:0;width:300px;height:300px;background:{LIME};clip-path:polygon(0 0,100% 0,0 100%)}}
.w{{fill:#2A1A99}}
.brand{{position:absolute;top:270px;right:90px;display:flex;align-items:center;gap:16px}}
.mark{{width:52px;height:66px;background:#fff;border-radius:0 33px 33px 0;position:relative}}
.mark i{{position:absolute;left:18px;top:15px;width:17px;height:36px;background:{NAVY};border-radius:0 18px 18px 0}}
.brand b{{font-size:30px;font-weight:700;letter-spacing:9px;direction:ltr}}
.tag{{display:flex;align-items:center;gap:12px;background:{LIME};color:{NAVY};border-radius:999px;padding:8px 28px 12px;font-size:36px;font-weight:700;margin-right:14px}}
.main{{position:absolute;top:390px;right:90px;left:90px;display:flex;flex-direction:column;gap:34px}}
.chip{{align-self:flex-start;display:flex;align-items:center;gap:16px;background:rgba(255,255,255,.1);border:2px solid rgba(211,216,62,.6);border-radius:999px;padding:12px 32px 16px;font-size:40px;font-weight:600}}
.dot{{width:18px;height:18px;border-radius:50%;background:{LIME};box-shadow:0 0 0 8px rgba(211,216,62,.25)}}
h1{{font-size:190px;font-weight:700;line-height:1.02}} h1 span,h2 span{{color:{LIME}}}
h2{{font-size:96px;font-weight:700;line-height:1.2}}
.sub{{font-size:50px;font-weight:600;line-height:1.5;color:#DAD6F5;white-space:pre-line}}
.ask{{background:#fff;color:{NAVY};border-radius:36px;padding:34px 40px 30px;box-shadow:0 30px 70px rgba(8,0,60,.5);border-top:12px solid {LIME}}}
.ask .q{{font-size:50px;font-weight:700;line-height:1.35}}
.ask .hint{{margin-top:18px;height:120px;border:3px dashed #C9C4EE;border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:32px;color:#8A84B8}}
.cover{{align-self:center;width:470px;transform:rotate(-3deg);border-radius:24px;overflow:hidden;box-shadow:0 40px 90px rgba(8,0,60,.6);border:8px solid #fff}}
.cover img{{display:block;width:100%}}
.go{{align-self:center;background:{LIME};color:{NAVY};border-radius:999px;padding:18px 54px 24px;font-size:48px;font-weight:700}}
.foot{{position:absolute;top:1460px;left:50%;transform:translateX(-50%);white-space:nowrap;background:{DEEP};border:2px solid rgba(211,216,62,.6);border-radius:999px;padding:10px 34px 14px;font-size:32px;font-weight:600;color:#fff}}
</style></head><body><div class="pat"></div><div class="corner"></div>{SKY}
<div class="brand" id="br"><div class="mark"><i></i></div><b>DINARY</b><div class="tag"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="{NAVY}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>السوق العقاري</div></div>
<div class="main">{body}</div>
{('<div class="foot" id="ft">'+cfg['foot']+'</div>') if cfg.get('foot') else ''}
<script>
const cl=x=>Math.min(Math.max(x,0),1), back=x=>{{x=cl(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);}};
const SEC={SEC};
function show(id,a){{const e=document.getElementById(id);if(!e)return;const p=back((window.t-a)/.5);e.style.opacity=cl((window.t-a)/.2);
  e.style.transform=(id==='a3'&&{str(not teaser).lower()}?'rotate(-3deg) ':'')+`translateY(${{(1-p)*60}}px) scale(${{.9+.1*p}})`;}}
function render(t){{window.t=t;
  document.querySelectorAll('.s').forEach(s=>s.style.opacity=.35+.65*Math.abs(Math.sin(2*Math.PI*2*t/SEC+ +s.dataset.p)));
  document.querySelectorAll('.b').forEach(g=>{{const p=back((t-.05*g.dataset.i)/.6);g.style.transform=`translateY(${{(1-p)*500}}px)`;}});
  document.querySelectorAll('.w').forEach(r=>{{const on=t>=+r.dataset.t;r.style.fill=on?'#E4E86A':'#2A1A99';r.style.filter=on?'drop-shadow(0 0 8px rgba(211,216,62,.9))':'none';}});
  show('br',.2); show('a1',.5); show('a2',.8); show('a3',1.3); show('a4',1.8); const ft=document.getElementById('ft'); if(ft){{ show('ft',2.2); ft.style.transform='translateX(-50%) '+ft.style.transform; }}
}}
render(0);
</script></body></html>"""

async def main():
    tmp = OUT.parent / (OUT.name + "_frames"); tmp.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME) if CHROME else await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(HTML); await pg.evaluate("document.fonts.ready.then(()=>1)"); await pg.wait_for_timeout(300)
        await pg.evaluate(f"render({SEC})")
        await pg.screenshot(path=str(OUT) + ".jpg", type="jpeg", quality=92)
        for f in range(int(FPS * SEC)):
            await pg.evaluate(f"render({f / FPS})")
            await pg.screenshot(path=str(tmp / f"f{f:04d}.jpg"), type="jpeg", quality=90)
        await b.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-movflags", "+faststart", str(OUT) + ".mp4"], check=True)
    shutil.rmtree(tmp)
    print(str(OUT) + ".jpg", str(OUT) + ".mp4", "ok")

asyncio.run(main())
