# Sweeps Intelligence

Technical recon of the Casino Masterlist: 102 sites surveyed, 95 active, 7 closed.
Prepared by Santiago.

## Deploy

`site/index.html` is one self-contained file. Put it at the root of any static host
(Vercel, Netlify, GitHub Pages). No build step. Fonts load from Google Fonts and fall back
to system fonts if blocked.

## What the page contains (one tab each)

| Tab | What it shows |
|---|---|
| Overview | The daily flow in four steps, key findings, expected daily yield by tier |
| Platform map | 13 parent companies running 41 sites, one adapter each, as a unit chart and a table |
| Claim types | The seven ways a site hands out its daily bonus, with bot behaviour for each |
| Architecture | Seven-stage diagram, one claim step by step, and the outcome table (what the bot does on each failure) |
| Site directory | All 95 active sites, searchable, filterable by tier, sortable |
| Risk and payout | Site health, difficulty distribution, days to first payout, what the analysis cannot see |
| Build plan | Two phases, week-1 checks, and the adapter and config code |

Every section pairs an "In plain English" block with a "Technical" block.

## Key numbers

| Metric | Value |
|---|---|
| Active sites | 95 |
| Adapters needed | 67 (28 saved by grouping 41 sites into 13 families) |
| Expected yield | $58.74 per day, about $1,762 per month (floor $30.90, ceiling $123.70) |
| Median time to first payout | 227 days |

Yield method: 70% of each site's minimum plus 30% of its maximum. Each maximum is capped at
$5.00 per site per day, because 8 sites list larger figures that come from purchase packs or
jackpot-wheel prizes rather than the standard daily claim.

## Files

- `site/index.html` the dashboard
- `site/files/adapter_interface.py` base adapter class and a full B2 example
- `site/files/config.example.json` scheduler, anti-detection, vault, alerts and sample sites
- `src/data.py` all 102 sites from the masterlist
- `src/analyze.py` families, claim types, difficulty, yield and health
- `src/render.py` generates the dashboard
- `data/analysis.json` analysis output

## Regenerate

```bash
cd src
python3 render.py   # writes site/index.html and data/analysis.json
```

Python 3.8 or newer, no external dependencies.
