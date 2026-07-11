<samp>[🇰🇷 한국어](README.md) · 🇺🇸 English</samp>

# ir-search

> ⚠️ **This skill covers South Korean government / public-agency support programs only.** It does not cover programs from any other country, and the announcements it processes are written in Korean.

A Claude Code skill for **exhaustive surveys of Korean government support programs** (startup grants, commercialization funding, incubation space, R&D calls, vouchers, competitions).

It crawls every currently-open announcement from K-Startup, Bizinfo, NIPA, KOCCA, and SMTECH, matches them against the profile of the project in your working folder — founding stage, region, needs (funding / space / R&D) — verifies eligibility against the original announcement text, and produces a report with a three-tier classification:

- **Group A — Apply right now**: eligible as-is (sorted by deadline, imminent ones flagged)
- **Group B — Unlocked by a requirement (roadmap)**: triggers like incorporation or securing investment, with chained paths spelled out (e.g., competition prize → non-metro incorporation → Pre-TIPS → TIPS)
- **Group C — Eligible with reframing**: concrete angles for re-describing your item in another domain's language (content production, social services, art×tech, ...)

Why exhaustive review instead of keyword search: the programs an "AI startup" can actually win — content-production grants, art×tech residencies, social-service startup funds — never match the keyword "AI".

## Covered sources

| Source | What it is | Crawler |
|---|---|---|
| [K-Startup](https://www.k-startup.go.kr) | Unified startup-support portal (default) | `kstartup_crawl.py` |
| [Bizinfo](https://www.bizinfo.go.kr) | All-ministry/region SME support (widest coverage) | `sources_crawl.py` |
| [NIPA](https://www.nipa.kr) | AI / ICT programs | `sources_crawl.py` |
| [KOCCA](https://www.kocca.kr) | Content-industry programs | `sources_crawl.py` |
| [SMTECH](https://www.smtech.go.kr) | SME R&D calls | `sources_crawl.py` |

More sources (NIA, IITP, IRIS, regional agencies) are catalogued in `references/sources.md`.

## Install

```bash
git clone https://github.com/djfksjd/ir-search.git ~/.claude/skills/ir-search
pip install 'curl_cffi>=0.15'   # recommended (avoids TLS-fingerprint blocking)
```

## Use

With your project folder open in Claude Code:

```
우리 아이템에 맞는 지원사업 전수조사 해줘
(Survey the support programs that fit this project)
```

or `/ir-search`. Claude reads the project context from the folder and asks only for the missing profile fields (founding stage, region, needs) before starting.

The crawlers also work standalone:

```bash
python3 scripts/kstartup_crawl.py list -o all.jsonl            # all open K-Startup announcements
python3 scripts/kstartup_crawl.py detail 178481 -o details/    # K-Startup detail pages
python3 scripts/sources_crawl.py list bizinfo -o biz.jsonl     # Bizinfo
python3 scripts/sources_crawl.py list all -o sources.jsonl     # all four extra sources
python3 scripts/sources_crawl.py detail <URL> -o details/      # detail page from any source
```

## Layout

```
ir-search/
├── SKILL.md                    # workflow (profile → collect all → review all → verify → 3-tier report)
├── scripts/
│   ├── kstartup_crawl.py       # K-Startup crawler
│   └── sources_crawl.py        # Bizinfo / NIPA / KOCCA / SMTECH crawler
└── references/sources.md       # source registry (verified access recipes + secondary sources)
```

Note: `SKILL.md` is written in Korean — the whole domain (announcements, eligibility criteria, report vocabulary) is Korean, and the model works with it natively.

## Caveats

- Announcement details (deadlines, eligibility, amounts) change frequently. **Always confirm with the accepting agency before applying.** The report reflects the announcement text at survey time.
- Only public announcement pages are accessed, with a delay between requests. Please respect the target sites' terms of service.

## License

MIT
