import asyncio, pathlib, sys, shutil, subprocess, base64, random, json
from playwright.async_api import async_playwright

# Short animated reel (1080x1920, 30 fps) in the «السوق العقاري» theme.
# usage: python3 tool/reel_aqari.py <reel.json> <out.mp4>
# reel.json: {"kicker","title","title2","num","num_label","source","end_title","end_sub","seconds"}
BASE = pathlib.Path(__file__).resolve().parent
FD = BASE / "fonts"
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2])
FPS, SEC = 30, float(cfg.get("seconds", 10))
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
AR = "U+0600-06FF,U+0750-077F,U+0870-08FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFC"
LA = "U+0000-00FF,U+2000-206F,U+20AC,U+2212"
def furl(p): return "data:font/woff2;base64," + base64.b64encode((FD / p).read_bytes()).decode()
faces = "".join(f"@font-face{{font-family:{fam};font-weight:{w};src:url({furl(f'{file}-{s}-{w}-normal.woff2')});unicode-range:{r}}}"
                for fam, file, ws in (("H", "el-messiri", (700,)), ("B", "readex-pro", (400, 600, 700)))
                for w in ws for s, r in (("arabic", AR), ("latin", LA)))
SAND, BRASS, NIGHT = "#F3EBDD", "#C9A25E", "#0D2236"

random.seed(7)
blds = [(x,1740-h,w,h) for x,w,h in [(0,170,300),(170,140,380),(310,190,260),(500,130,420),(630,170,330),(800,150,280),(950,130,360)]]
svg = []
for i,(x,y,w,h) in enumerate(blds):
    wins = []
    for wy in range(y+34, y+h-40, 52):
        for wx in range(x+24, x+w-34, 38):
            wins.append(f'<rect class="w" data-t="{random.uniform(3.0,5.6):.2f}" x="{wx}" y="{wy}" width="18" height="26" rx="2"/>')
    svg.append(f'<g class="b" data-i="{i}"><rect x="{x+6}" y="{y}" width="{w-12}" height="{h}" fill="#0F2A40" stroke="{BRASS}" stroke-width="3"/>{"".join(wins)}</g>')
SKY = f'<svg id="sky" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">{"".join(svg)}<line x1="0" y1="1740" x2="1080" y2="1740" stroke="{BRASS}" stroke-width="4"/></svg>'

HTML = f"""<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:B;color:#fff;
background:linear-gradient(170deg,#163A55 0%,{NIGHT} 50%,#081624 100%)}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(201,162,94,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(201,162,94,.08) 1px,transparent 1px),linear-gradient(rgba(201,162,94,.12) 2px,transparent 2px),linear-gradient(90deg,rgba(201,162,94,.12) 2px,transparent 2px);background-size:40px 40px,40px 40px,200px 200px,200px 200px}}
.w{{fill:#1B3A55}}
#top{{position:absolute;top:210px;right:90px;left:90px;display:flex;flex-direction:column;gap:30px}}
.tag{{align-self:flex-start;display:flex;gap:14px;align-items:center;border:3px solid {BRASS};color:{BRASS};border-radius:999px;padding:8px 30px 12px;font-family:H;font-size:44px;font-weight:700}}
.k{{font-size:38px;color:{BRASS};font-weight:600}}
h1{{font-family:H;font-size:110px;line-height:1.2;font-weight:700}} h1 span{{color:{BRASS}}}
#num{{font-size:260px;font-weight:700;color:{BRASS};line-height:1;direction:ltr;text-align:right;letter-spacing:-6px}}
.nl{{font-size:50px;font-weight:600;color:{SAND};line-height:1.4}}
.src{{font-size:30px;color:#9FB3C4}}
#end{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;text-align:center;background:rgba(8,22,36,.88)}}
#end h2{{font-family:H;font-size:96px;color:{BRASS}}} #end p{{font-size:46px;color:{SAND};white-space:pre-line;line-height:1.5}}
.logo{{display:flex;align-items:center;gap:16px;direction:ltr;font-size:46px;font-weight:600;margin-top:30px}}
.mark{{width:46px;height:60px;background:#fff;border-radius:0 30px 30px 0;position:relative}}
.mark i{{position:absolute;left:16px;top:14px;width:15px;height:32px;background:{NIGHT};border-radius:0 16px 16px 0}}
</style></head><body><div id="grid"></div>{SKY}
<div id="top">
 <div class="tag" id="tag"><svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="{BRASS}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>السوق العقاري</div>
 <div class="k" id="k">{cfg['kicker']}</div>
 <h1 id="t">{cfg['title']}<br><span>{cfg['title2']}</span></h1>
 <div id="num">0</div>
 <div class="nl" id="nl">{cfg['num_label']}</div>
 <div class="src" id="src">{cfg['source']}</div>
</div>
<div id="end"><h2>{cfg['end_title']}</h2><p>{cfg['end_sub']}</p><div class="logo"><div class="mark"><i></i></div>dinary.iq</div></div>
<script>
const ease=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
const seg=(t,a,b)=>ease((t-a)/(b-a));
const NUM={cfg['num']};
function render(t){{
  document.querySelectorAll('.b').forEach(g=>{{const i=+g.dataset.i;const p=seg(t,0.2+i*0.18,1.6+i*0.18);
    g.style.transform=`translateY(${{(1-p)*900}}px)`;}});
  document.querySelectorAll('.w').forEach(r=>{{const on=t>=+r.dataset.t;r.style.fill=on?'#E8C77E':'#1B3A55';
    r.style.filter=on?'drop-shadow(0 0 8px rgba(232,199,126,.9))':'none';}});
  const show=(id,a,b)=>{{const p=seg(t,a,b);const el=document.getElementById(id);el.style.opacity=p;el.style.transform=`translateY(${{(1-p)*40}}px)`;}};
  show('tag',0.4,1.2); show('k',1.6,2.4); show('t',2.0,3.0); show('num',4.4,5.0); show('nl',5.4,6.2); show('src',6.0,6.8);
  const c=seg(t,4.4,6.4); document.getElementById('num').textContent=(NUM*c).toFixed(1);
  const e=seg(t,{SEC-2.4},{SEC-1.6}); const end=document.getElementById('end'); end.style.opacity=e; end.style.transform=`scale(${{0.96+0.04*e}})`;
}}
render(0);
</script></body></html>"""

async def main():
    tmp = OUT.parent / (OUT.stem + "_frames"); tmp.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME) if CHROME else await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(HTML); await pg.evaluate("document.fonts.ready.then(()=>1)"); await pg.wait_for_timeout(300)
        n = int(FPS * SEC)
        for f in range(n):
            await pg.evaluate(f"render({f / FPS})")
            await pg.screenshot(path=str(tmp / f"f{f:04d}.jpg"), type="jpeg", quality=90)
        await b.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-movflags", "+faststart", str(OUT)], check=True)
    shutil.rmtree(tmp)
    print(OUT, "ok")

asyncio.run(main())
