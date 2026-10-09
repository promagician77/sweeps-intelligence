# Sweeps Intelligence — Site Automation Recon

Technical intelligence report covering **102 sweepstakes casino sites** (95 active, 7 dead), built from the client's master spreadsheet.

## What's Inside

### `site/index.html` — Interactive Dashboard
Open in any browser. Contains:
- **Platform Family Map** — 13 parent companies running 41 sites. One adapter per family = 28 fewer adapters to build and maintain.
- **Mechanism Taxonomy** — Every bonus type classified (Click, Wheel, Streak, Timed, Multi-step, Purchase-locked, VIP-locked) with adapter implementation hints.
- **Architecture Blueprint** — SVG diagram: Scheduler → Orchestrator → Anti-Detection → Browser Pool → Adapter Layer → Data Layer.
- **Site Health Matrix** — 85 healthy / 10 risky / 7 dead, with risk reasons.
- **Revenue Projections** — $90.84/day expected ($2,725/month) across all active sites, broken down by tier.
- **Full Site Directory** — Searchable, filterable, sortable table of all 95 active sites with tier, mechanism, parent, difficulty score, and daily SC range.

### `site/files/adapter_interface.py` — Adapter Pattern
Production-ready Python: abstract `SiteAdapter` base class + concrete `B2Adapter` covering 6 sites. Shows the exact contract every platform adapter implements (login → claim_daily → check_balance → is_healthy → cleanup).

### `site/files/config.example.json` — Config Format
Full bot configuration: scheduler timing, anti-detection settings (fingerprint rotation, residential proxies, human-like delays), encrypted credential vault, monitoring/alerting (Telegram + Discord), and 4 example site definitions showing how sites map to adapters.

### `src/data.py` — Site Database
All 102 sites with: name, tier (GOD/HIGH/MED/TRASH/DEAD), parent company, mechanism type, daily SC range, minimum redemption, restricted states, operational notes.

### `src/analyze.py` — Analysis Engine
Platform family grouping, mechanism taxonomy, difficulty scoring (1-5 scale), revenue projections, and site health classification.

## Key Numbers

| Metric | Value |
|--------|-------|
| Active sites | 95 |
| Dead sites | 7 |
| Platform families (multi-site) | 13 |
| Unique adapters needed | 67 |
| Adapters saved by family grouping | 28 |
| Expected daily SC | $90.84 |
| Expected monthly SC | $2,725.20 |

## Architecture

```
                    ┌─────────────┐
                    │  Scheduler   │  cron daily + interval (Fliff 2h, Jefebet 6h)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Orchestrator │  iterates sites, manages retries
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼───┐ ┌──────▼──────┐
       │Anti-Detection│ │Proxy │ │  Credential  │
       │  fingerprint │ │resi  │ │    Vault     │
       │  + delays    │ │sticky│ │  (encrypted) │
       └──────┬──────┘ └──┬───┘ └──────┬──────┘
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │ Browser Pool │  Playwright, 1 context per site
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
  ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
  │ B2Adapter  │     │VGWAdapter │     │FliffAdapter│  ...67 total
  │ (6 sites)  │     │ (4 sites) │     │ (1 site)  │
  └────────────┘     └───────────┘     └───────────┘
```

## Running the Analysis

```bash
cd src
python3 render.py       # generates site/index.html + data/analysis.json
python3 analyze.py      # standalone analysis to data/analysis.json
```

Requires Python 3.8+, no external dependencies.
