import asyncio, pathlib, sys, shutil, subprocess, base64, random, json, wave, math, struct
from playwright.async_api import async_playwright

# Animated reel (1080x1920, 30 fps) in the «السوق العقاري» theme, with a hook, kinetic text,
# a live night city (crane, cars, twinkling stars) and a generated soundtrack (no licensed music).
# usage: python3 tool/reel_aqari.py <reel.json> <out.mp4>
# reel.json: {"hook1","hook2","beat","count_pre","num","num_label","why1","why2","ask","ask_sub","source","seconds"}
BASE = pathlib.Path(__file__).resolve().parent
FD = BASE / "fonts"
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text())
OUT = pathlib.Path(sys.argv[2])
FPS, SEC = 30, float(cfg.get("seconds", 13))
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
AR = "U+0600-06FF,U+0750-077F,U+0870-08FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFC"
LA = "U+0000-00FF,U+2000-206F,U+20AC,U+2212"
def furl(p): return "data:font/woff2;base64," + base64.b64encode((FD / p).read_bytes()).decode()
faces = "".join(f"@font-face{{font-family:{fam};font-weight:{w};src:url({furl(f'{file}-{s}-{w}-normal.woff2')});unicode-range:{r}}}"
                for fam, file, ws in (("H", "ibm-plex-sans-arabic", (700,)), ("B", "ibm-plex-sans-arabic", (400, 600, 700)))
                for w in ws for s, r in (("arabic", AR), ("latin", LA)))
SAND, BRASS, NIGHT = "#FFFFFF", "#D3D83E", "#200F8C"
# timeline (seconds)
T = dict(h1=0.0, h2=0.7, beat=1.7, rise=2.4, cnt=4.4, cnt_end=6.4, why=7.0, ask=9.4, end=SEC - 1.4)

random.seed(11)
GROUND = 1760
blds = [(x, GROUND - h, w, h) for x, w, h in
        [(-10,160,330),(150,130,430),(280,180,280),(460,140,480),(600,170,360),(770,150,300),(920,170,400)]]
svg = []
for i, (x, y, w, h) in enumerate(blds):
    wins = [(f'<rect class="w" data-base="1" data-t="0" x="{wx}" y="{wy}" width="18" height="26" rx="2"/>' if random.random() < .35 else
             f'<rect class="w" data-t="{random.uniform(T["cnt"]-0.4, T["cnt_end"]+0.4):.2f}" data-off="{random.uniform(SEC-1.2, SEC-0.3):.2f}" x="{wx}" y="{wy}" width="18" height="26" rx="2"/>')
            for wy in range(y + 34, y + h - 40, 52) for wx in range(x + 24, x + w - 34, 38)]
    svg.append(f'<g class="b" data-i="{i}"><rect x="{x+6}" y="{y}" width="{w-12}" height="{h}" fill="#1A0B7A" stroke="{BRASS}" stroke-width="3"/>{"".join(wins)}</g>')
# crane on the tallest building (index 3)
cx, cy = 530, GROUND - 480
crane = (f'<g id="crane" class="b" data-i="3"><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-150}" stroke="{BRASS}" stroke-width="5"/>'
         f'<g id="arm" style="transform-origin:{cx}px {cy-150}px"><line x1="{cx-60}" y1="{cy-150}" x2="{cx+230}" y2="{cy-150}" stroke="{BRASS}" stroke-width="5"/>'
         f'<line x1="{cx+180}" y1="{cy-150}" x2="{cx+180}" y2="{cy-60}" stroke="{SAND}" stroke-width="2"/>'
         f'<rect x="{cx+160}" y="{cy-60}" width="40" height="26" fill="{BRASS}"/></g></g>')
stars = "".join(f'<circle class="s" data-p="{random.uniform(0,6.28):.2f}" cx="{random.randint(20,1060)}" cy="{random.randint(60,900)}" r="{random.choice([1.5,2,2.5])}" fill="#fff"/>'
                for _ in range(70))
cars = "".join(f'<g class="car" data-o="{o}" data-v="{v}"><rect x="0" y="{GROUND+14}" width="70" height="10" rx="5" fill="#D3D83E"/>'
               f'<circle cx="64" cy="{GROUND+19}" r="9" fill="rgba(255,240,200,.9)"/></g>' for o, v in ((0, 3), (520, 4), (900, 2)))
SKY = (f'<svg id="sky" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">{stars}'
       f'<circle cx="170" cy="1040" r="62" fill="#F3EBDD" opacity=".85"/><circle cx="196" cy="1024" r="56" fill="#24109A"/>'
       f'<clipPath id="cut"><rect x="-200" y="0" width="1480" height="{GROUND}"/></clipPath><g id="city" clip-path="url(#cut)">{"".join(svg)}{crane}</g><line x1="0" y1="{GROUND}" x2="1080" y2="{GROUND}" stroke="{BRASS}" stroke-width="4"/>{cars}</svg>')

HTML = f"""<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:B;color:#fff;
background:radial-gradient(circle at 50% 35%,#3A27C4 0%,{NIGHT} 50%,#120565 100%)}}
#cam{{position:absolute;inset:0;transform-origin:50% 75%}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(201,162,94,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(201,162,94,.07) 1px,transparent 1px);background-size:40px 40px}}
.w{{fill:#2A1A99}}
.scene{{position:absolute;left:80px;right:80px;top:300px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:26px}}
.big{{font-family:H;font-weight:700;font-size:150px;line-height:1.15}}
.gold{{color:{BRASS}}}
.mid{{font-size:62px;font-weight:600;color:{SAND};line-height:1.4;white-space:pre-line}}
#num{{font-size:300px;font-weight:700;color:{BRASS};line-height:1;direction:ltr;letter-spacing:-8px}}
.src{{font-size:30px;color:#B9B3E6}}
.eq{{display:flex;flex-direction:column;align-items:center;gap:18px}}
.pill{{border:4px solid {BRASS};border-radius:26px;padding:16px 40px 24px;font-size:64px;font-weight:700}}
.up{{font-size:110px;color:{BRASS};font-weight:700;line-height:1}}
.tag{{position:absolute;top:120px;right:80px;display:flex;gap:14px;align-items:center;border:3px solid {BRASS};color:{BRASS};border-radius:999px;padding:8px 30px 12px;font-family:H;font-size:42px;font-weight:700}}
.cmt{{display:flex;align-items:center;gap:22px;background:{BRASS};color:{NIGHT};border-radius:40px 40px 8px 40px;padding:26px 40px;font-size:54px;font-weight:700;box-shadow:0 20px 50px rgba(0,0,0,.4)}}
.opts{{display:flex;gap:28px}}
.opt{{border:4px solid {BRASS};border-radius:999px;padding:14px 46px 20px;font-size:60px;font-weight:700;color:{SAND}}}
.logo{{position:absolute;bottom:60px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:16px;direction:ltr;font-size:40px;font-weight:600}}
.mark{{width:40px;height:52px;background:#fff;border-radius:0 26px 26px 0;position:relative}}
.mark i{{position:absolute;left:14px;top:12px;width:13px;height:28px;background:{NIGHT};border-radius:0 14px 14px 0}}
</style></head><body><div id="cam"><div id="grid"></div>{SKY}</div>
<div class="tag" id="tag"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="{BRASS}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>السوق العقاري</div>
<div class="scene" id="s1"><div class="big" id="h1">{cfg['hook1']}</div><div class="big gold" id="h2">{cfg['hook2']}</div><div class="mid" id="beat">{cfg['beat']}</div></div>
<div class="scene" id="s2"><div class="mid" id="pre">{cfg['count_pre']}</div><div id="num">0</div><div class="mid" id="nl">{cfg['num_label']}</div><div class="src" id="src">{cfg['source']}</div></div>
<div class="scene" id="s3"><div class="eq"><div class="pill" id="w1">{cfg['why1']}</div><div class="up" id="arrow">↓</div><div class="pill" id="w2" style="color:{BRASS}">{cfg['why2']}</div></div></div>
<div class="scene" id="s4"><div class="cmt" id="ask">{cfg['ask']}</div><div class="opts"><div class="opt" id="o1">{cfg.get("opts",["مِلك","إيجار","ويا الأهل"])[0]}</div><div class="opt" id="o2">{cfg.get("opts",["مِلك","إيجار","ويا الأهل"])[1]}</div><div class="opt" id="o3">{cfg.get("opts",["مِلك","إيجار","ويا الأهل"])[2]}</div></div><div class="mid" id="asub">{cfg['ask_sub']}</div></div>
<div class="logo" id="logo"><div class="mark"><i></i></div>dinary.iq</div>
<script>
const cl=x=>Math.min(Math.max(x,0),1), ease=x=>1-Math.pow(1-cl(x),3);
const back=x=>{{x=cl(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);}};
const seg=(t,a,d)=>ease((t-a)/d), pop=(t,a,d)=>back((t-a)/d);
const T={json.dumps(T)}, NUM={cfg['num']}, SEC={SEC}, DEC={cfg.get('decimals',1)};
function vis(id,a,b){{const o=Math.min(seg(window.t,a,.35),1-seg(window.t,b,.3));document.getElementById(id).style.opacity=o;return o;}}
function popIn(id,a){{const e=document.getElementById(id);const p=pop(window.t,a,.45);e.style.transform=`scale(${{.4+.6*p}})`;e.style.opacity=cl((window.t-a)/.15);}}
function render(t){{window.t=t;
  const z=1+.07*Math.sin(Math.PI*t/SEC), sh=(Math.abs(t-T.beat)<.12||Math.abs(t-T.why)<.12)?Math.sin(t*90)*6:0;
  document.getElementById('cam').style.transform=`scale(${{z}}) translateX(${{sh}}px)`;
  document.querySelectorAll('.s').forEach(s=>s.style.opacity=.35+.65*Math.abs(Math.sin(2*Math.PI*3*t/SEC+ +s.dataset.p)));
  document.querySelectorAll('.b').forEach(g=>{{g.style.transform='none';}});
  document.getElementById('arm').style.transform=`rotate(${{Math.sin(2*Math.PI*2*t/SEC)*7}}deg)`;
  document.querySelectorAll('.w').forEach(r=>{{const on=r.dataset.base?true:(t>=+r.dataset.t && t<+r.dataset.off);r.style.fill=on?'#E4E86A':'#2A1A99';r.style.filter=on?'drop-shadow(0 0 8px rgba(211,216,62,.9))':'none';}});
  document.querySelectorAll('.car').forEach(c=>{{const x=((+c.dataset.o + t*1240*(+c.dataset.v)/SEC)%1240)-120;c.setAttribute('transform',`translate(${{x}},0)`);}});
  const s1=document.getElementById('s1'); s1.style.opacity=Math.max(1-seg(t,T.rise+.3,.3), seg(t,SEC-.45,.4)); const h1=document.getElementById('h1'); h1.style.opacity=1; h1.style.transform='none'; ['h2','beat'].forEach(id=>{{if(t>SEC-1)document.getElementById(id).style.opacity=0;}}); if(t<SEC-1){{popIn('h2',T.h2); popIn('beat',T.beat);}}
  vis('s2',T.cnt-.3,T.why-.2); popIn('pre',T.cnt-.3); popIn('num',T.cnt);
  const c=seg(t,T.cnt,T.cnt_end-T.cnt); document.getElementById('num').textContent=(NUM*c).toFixed(DEC);
  popIn('nl',T.cnt_end-.5); popIn('src',T.cnt_end);
  vis('s3',T.why-.1,T.ask-.2); popIn('w1',T.why); popIn('w2',T.why+.9);
  const ar=document.getElementById('arrow'); ar.style.opacity=cl((t-T.why-.5)/.2); ar.style.transform=`translateY(${{Math.sin(t*10)*10}}px)`;
  vis('s4',T.ask-.1,SEC-.75); popIn('ask',T.ask); popIn('o1',T.ask+.6); popIn('o2',T.ask+.8); popIn('o3',T.ask+1.0); popIn('asub',T.ask+1.5);
  document.getElementById('tag').style.opacity=1;
  document.getElementById('logo').style.opacity=Math.min(cl((t-T.ask)/.4),1-seg(t,SEC-.75,.3));
}}
render(0);
</script></body></html>"""

def soundtrack(path):
    # Original generated audio: warm pad chords, whooshes on scene cuts, ticks while the number counts.
    sr, n = 44100, int(44100 * SEC)
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (164.81, 207.65, 246.94)]
    hits = [SEC - .45, T["h2"], T["beat"], T["rise"], T["cnt"], T["why"], T["why"] + .9, T["ask"]]
    random.seed(3)
    buf = bytearray()
    for i in range(n):
        t = i / sr
        ch = chords[int(t / (SEC / 4)) % 4]
        env = 1.0
        pad = sum(math.sin(2 * math.pi * f * t) + .3 * math.sin(4 * math.pi * f * t) for f in ch) * .045 * env
        bass = math.sin(math.pi * ch[0] * t) * .08 * env * (0.6 + 0.4 * math.sin(2 * math.pi * t) ** 2)
        s = pad + bass
        for h in hits:
            d = t - h
            if 0 <= d < .35:
                s += (random.uniform(-1, 1) * .25 + math.sin(2 * math.pi * (90 + 400 * d) * t) * .2) * math.exp(-d * 12)
        if T["cnt"] <= t <= T["cnt_end"]:
            s += math.sin(2 * math.pi * 1800 * t) * .12 * math.exp(-((t - T["cnt"]) % 0.1) * 120)
        s = max(-1, min(1, s))
        v = int(s * 30000)
        buf += struct.pack('<hh', v, v)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(buf))

async def main():
    tmp = OUT.parent / (OUT.stem + "_frames"); tmp.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME) if CHROME else await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(HTML); await pg.evaluate("document.fonts.ready.then(()=>1)"); await pg.wait_for_timeout(300)
        for f in range(int(FPS * SEC)):
            await pg.evaluate(f"render({f / FPS})")
            await pg.screenshot(path=str(tmp / f"f{f:04d}.jpg"), type="jpeg", quality=90)
        await b.close()
    wav = tmp / "a.wav"; soundtrack(wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.jpg"), "-i", str(wav),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(OUT)], check=True)
    shutil.rmtree(tmp)
    print(OUT, "ok")

asyncio.run(main())
