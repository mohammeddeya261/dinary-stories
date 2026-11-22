# Dinary · اقتصاد اليوم — automation runbook

Instagram stories for **@dinary.iq** (Windsor.ai Social Media connector, connector `instagram`,
account id `17841404495582696`, action `create_story` with `image_url`).
Facebook is covered by Instagram's own "share story to Facebook" setting.

Timezone: Asia/Baghdad (UTC+3). All dates in Arabic: e.g. «الأحد 22 تشرين الثاني 2026».

## Setup in a fresh session
1. Clone this repo (attach `mohammeddeya261/dinary-stories` with push access if needed).
2. `pip install --break-system-packages playwright pillow` if missing; Chrome/Chromium must exist
   (`which google-chrome`), otherwise `python3 -m playwright install chromium`.
3. Generator: `python3 tool/make.py <content.json> <out_dir> <prefix>` → JPEGs 1080×1920.
   Content format: see `tool/example.json`. Fields: `date`, `handle` (always `@dinary.iq`),
   optional `pill` (default «اقتصاد اليوم»; use «عاجل» for breaking), optional `cover` (false = no cover),
   `news[]` each with `short` (cover line), `tag`, `title` (≤ ~45 chars), `stat`, `stat_label`,
   `body` (1–2 sentences), `angle` (one-line «زاوية اقتصادية»), `source`.
   Layouts vary automatically (navy, lime, split, light; plus `quote` for statements — set
   `"layout":"quote"`, `"quote"` (paraphrase, marked «بتصرّف» in `speaker`) and `"speaker"`).
   Pick layouts so neighbouring stories differ; use `cover_layout` navy/lime to vary covers by day.
   Also vary wording and the «زاوية اقتصادية» line; avoid repeating the same phrasing every day.
4. Always open (Read) every rendered JPEG and check nothing overflows or overlaps the footer
   before publishing. Shorten text and re-render if it does.

## Editorial rules
- Topics: Iraq first (dollar/dinar in Baghdad & Erbil exchanges, CBI, oil exports & SOMO, budget,
  salaries, trade, investment, Kurdistan), then Middle East / Gulf / Hormuz / OPEC+ / oil prices
  when they affect Iraq.
- **Only news published today** (Baghdad date). Verify the date on the page. No old news.
- Trusted sources only: INA (ina.iq), Central Bank of Iraq (cbi.iq), Ministry of Oil, Shafaq News,
  Rudaw, Alsumaria, Al-Mada, Reuters, Bloomberg, AP, AFP, Asharq Business, Al Arabiya Business,
  OPEC. Cross-check numbers across 2 sources when possible. Never invent figures.
- Write in clear MSA with a light Iraqi tone; neutral, no political opinions.
- Paraphrase; never copy article text.
- Check `posted.log` and never post the same story twice.

## Publishing
- Commit JPEGs to `YYYY-MM-DD/` and push to `main`.
- Public URL: `https://raw.githubusercontent.com/mohammeddeya261/dinary-stories/main/<path>`.
  Confirm it returns HTTP 200 (`curl -sI`) before publishing.
- Publish each image with Windsor `execute_action` (connector `instagram`, account
  `17841404495582696`, action `create_story`, params `{"image_url": ...}`), in order, cover first.
- Append a line to `posted.log`: `<ISO time> | <file> | <title> | <media id>` and push.
