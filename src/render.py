"""
Generate the Site Intelligence Dashboard — an interactive HTML page
showing platform families, mechanism taxonomy, health, and architecture.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from analyze import run_analysis
from data import SITES, GOD, HIGH, MED, TRASH, DEAD
from data import CLICK, WHEEL, STREAK, TIMED, MULTI, LOCKED, VIP, MOBILE, NONE


def mech_icon(m):
    return {
        CLICK: "&#9745;", WHEEL: "&#9881;", STREAK: "&#9734;",
        TIMED: "&#9200;", MULTI: "&#8644;", LOCKED: "&#128274;",
        VIP: "&#9830;", MOBILE: "&#128241;", NONE: "&#10060;",
    }.get(m, "?")


def mech_label(m):
    return {
        CLICK: "Click", WHEEL: "Wheel", STREAK: "Streak",
        TIMED: "Timed", MULTI: "Multi-step", LOCKED: "Purchase-locked",
        VIP: "VIP-locked", MOBILE: "Mobile", NONE: "None",
    }.get(m, m)


def tier_class(t):
    return {"god": "tier-god", "high": "tier-high", "medium": "tier-med",
            "trash": "tier-trash", "dead": "tier-dead"}.get(t, "")


def difficulty_bar(d):
    pct = int(d / 5.0 * 100)
    cls = "diff-easy" if d <= 2.5 else "diff-med" if d <= 3.5 else "diff-hard"
    return f'<div class="diff-bar"><div class="diff-fill {cls}" style="width:{pct}%"></div><span>{d}</span></div>'


def render(results):
    s = results["summary"]
    r = results["revenue"]
    families = results["families"]
    mechs = results["mechanisms"]
    health = results["health"]
    diffs = results["difficulties"]

    # Multi-site families for the family map
    multi_fams = [f for f in families if f["count"] > 1]
    # Sort difficulties for the table
    diff_sorted = sorted(diffs, key=lambda x: x["name"])

    # Build mechanism breakdown cards
    mech_cards = ""
    ordered_mechs = [CLICK, WHEEL, STREAK, TIMED, MULTI, LOCKED, VIP]
    for m in ordered_mechs:
        if m not in mechs:
            continue
        info = mechs[m]
        count = len(info["sites"])
        mech_cards += f'''<div class="mech-card">
            <div class="mech-icon">{mech_icon(m)}</div>
            <div class="mech-name">{info["label"]}</div>
            <div class="mech-count">{count} site{"s" if count != 1 else ""}</div>
            <div class="mech-desc">{info["description"]}</div>
            <div class="mech-impl">
                <strong>Adapter method:</strong>
                {_adapter_hint(m)}
            </div>
        </div>'''

    # Family map table
    fam_rows = ""
    for f in multi_fams:
        sites_html = ", ".join(f["sites"])
        mechs_html = " ".join(
            f'<span class="mech-tag">{mech_icon(m)} {mech_label(m)}</span>'
            for m in f["mechanisms"]
        )
        fam_rows += f'''<tr>
            <td class="fam-name">{f["parent"]}</td>
            <td class="fam-count">{f["count"]}</td>
            <td class="fam-sites">{sites_html}</td>
            <td>{mechs_html}</td>
            <td class="fam-daily">${f["daily_min"]:.2f} – ${f["daily_max"]:.2f}</td>
            <td class="fam-saved">{f["adapters_saved"]}</td>
        </tr>'''

    # Health table — risky sites
    risk_rows = ""
    for r_site in health["risky"]:
        risk_rows += f'''<tr>
            <td>{r_site["name"]}</td>
            <td class="risk-reason">{r_site["reason"]}</td>
        </tr>'''

    dead_list = ", ".join(health["dead"]) if health["dead"] else "None"

    # All sites table
    all_rows = ""
    for site in SITES:
        if site["tier"] == DEAD:
            continue
        d = next((x for x in diffs if x["name"] == site["name"]), None)
        diff_val = d["difficulty"] if d else 0
        all_rows += f'''<tr class="{tier_class(site['tier'])}">
            <td>{site["name"]}</td>
            <td><span class="tier-badge {tier_class(site['tier'])}">{site["tier"].upper()}</span></td>
            <td>{site["parent"]}</td>
            <td>{mech_icon(site["mechanism"])} {mech_label(site["mechanism"])}</td>
            <td>${site["daily_min"]:.2f} – ${site["daily_max"]:.2f}</td>
            <td>${site["min_redeem"]}</td>
            <td>{difficulty_bar(diff_val)}</td>
        </tr>'''

    # Revenue by tier
    rev_rows = ""
    tier_order = [GOD, HIGH, MED, TRASH]
    tier_names = {GOD: "God", HIGH: "High", MED: "Medium", TRASH: "Trash"}
    for t in tier_order:
        td = r["by_tier"].get(t, {"count": 0, "daily_expected": 0})
        rev_rows += f'''<tr>
            <td><span class="tier-badge {tier_class(t)}">{tier_names[t]}</span></td>
            <td>{td["count"]}</td>
            <td>${td["daily_expected"]:.2f}</td>
            <td>${td["daily_expected"] * 30:.2f}</td>
        </tr>'''

    # Read adapter_interface.py for download
    adapter_path = os.path.join(os.path.dirname(__file__), "..", "site", "files", "adapter_interface.py")
    config_path = os.path.join(os.path.dirname(__file__), "..", "site", "files", "config.example.json")
    adapter_code = open(adapter_path).read()
    config_code = open(config_path).read()

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site Intelligence Report — Sweepstakes Automation</title>
<style>
:root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text2: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --amber: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
    --god: #ffd700;
    --high: #58a6ff;
    --med: #8b949e;
    --trash: #f85149;
    --dead: #484f58;
    --radius: 8px;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}}
@media (prefers-color-scheme: light) {{
    :root:not([data-theme="dark"]) {{
        --bg: #f6f8fa;
        --surface: #ffffff;
        --border: #d0d7de;
        --text: #1f2328;
        --text2: #656d76;
    }}
}}
:root[data-theme="dark"] {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text2: #8b949e;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--font);
        line-height: 1.6; padding: 16px; max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
h2 {{ font-size: 1.25rem; margin: 32px 0 12px; padding-bottom: 8px;
      border-bottom: 1px solid var(--border); color: var(--accent); }}
h3 {{ font-size: 1.05rem; margin: 16px 0 8px; }}
p, li {{ color: var(--text2); font-size: 0.9rem; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Metrics strip */
.metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px; margin: 20px 0; }}
.metric {{ background: var(--surface); border: 1px solid var(--border);
           border-radius: var(--radius); padding: 16px; text-align: center; }}
.metric .val {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
.metric .lbl {{ font-size: 0.78rem; color: var(--text2); margin-top: 4px; }}
.metric.highlight .val {{ color: var(--green); }}

/* Tables */
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem;
         background: var(--surface); border-radius: var(--radius);
         overflow: hidden; margin-bottom: 16px; }}
th {{ text-align: left; padding: 10px 12px; background: var(--bg);
      color: var(--text2); font-weight: 600; font-size: 0.78rem;
      text-transform: uppercase; letter-spacing: 0.5px;
      border-bottom: 2px solid var(--border); cursor: pointer; }}
th:hover {{ color: var(--accent); }}
td {{ padding: 8px 12px; border-bottom: 1px solid var(--border);
      vertical-align: middle; }}
tr:last-child td {{ border-bottom: none; }}

.fam-name {{ font-weight: 600; white-space: nowrap; }}
.fam-count {{ font-weight: 700; color: var(--accent); text-align: center; }}
.fam-saved {{ font-weight: 700; color: var(--green); text-align: center; }}
.fam-daily {{ white-space: nowrap; }}
.fam-sites {{ font-size: 0.8rem; color: var(--text2); }}

/* Tier badges */
.tier-badge {{ padding: 2px 8px; border-radius: 12px; font-size: 0.72rem;
               font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
.tier-god   {{ background: rgba(255,215,0,0.15); color: var(--god); }}
.tier-high  {{ background: rgba(88,166,255,0.15); color: var(--high); }}
.tier-med   {{ background: rgba(139,148,158,0.15); color: var(--med); }}
.tier-trash {{ background: rgba(248,81,73,0.15); color: var(--trash); }}
.tier-dead  {{ background: rgba(72,79,88,0.15); color: var(--dead); }}

/* Mechanism cards */
.mech-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
              gap: 12px; margin: 12px 0; }}
.mech-card {{ background: var(--surface); border: 1px solid var(--border);
              border-radius: var(--radius); padding: 16px; }}
.mech-icon {{ font-size: 1.6rem; margin-bottom: 4px; }}
.mech-name {{ font-weight: 700; font-size: 0.95rem; }}
.mech-count {{ color: var(--accent); font-size: 0.85rem; font-weight: 600; }}
.mech-desc {{ color: var(--text2); font-size: 0.8rem; margin: 8px 0; }}
.mech-impl {{ font-size: 0.78rem; color: var(--text2);
              background: var(--bg); padding: 8px; border-radius: 4px; margin-top: 8px; }}
.mech-tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px;
             font-size: 0.75rem; background: var(--bg); margin: 1px 2px;
             white-space: nowrap; }}

/* Difficulty bar */
.diff-bar {{ width: 100%; height: 18px; background: var(--bg);
             border-radius: 9px; position: relative; overflow: hidden;
             min-width: 80px; }}
.diff-fill {{ height: 100%; border-radius: 9px; transition: width 0.3s; }}
.diff-easy {{ background: var(--green); }}
.diff-med  {{ background: var(--amber); }}
.diff-hard {{ background: var(--red); }}
.diff-bar span {{ position: absolute; right: 6px; top: 0; font-size: 0.72rem;
                  font-weight: 700; line-height: 18px; color: var(--text); }}

.risk-reason {{ color: var(--amber); font-size: 0.82rem; }}

/* Architecture diagram */
.arch-box {{ background: var(--surface); border: 1px solid var(--border);
             border-radius: var(--radius); padding: 16px; margin: 12px 0;
             overflow-x: auto; }}
.arch-svg {{ width: 100%; max-width: 900px; margin: 0 auto; display: block; }}

/* Code download */
.code-section {{ background: var(--surface); border: 1px solid var(--border);
                 border-radius: var(--radius); margin: 12px 0; }}
.code-header {{ display: flex; justify-content: space-between; align-items: center;
                padding: 8px 12px; border-bottom: 1px solid var(--border); }}
.code-header span {{ font-weight: 600; font-size: 0.85rem; font-family: var(--mono); }}
.code-header button {{ background: var(--accent); color: #fff; border: none;
                       padding: 4px 12px; border-radius: 4px; cursor: pointer;
                       font-size: 0.78rem; }}
pre {{ padding: 12px; overflow-x: auto; font-size: 0.78rem; line-height: 1.5;
       font-family: var(--mono); max-height: 400px; overflow-y: auto; }}

/* Filter */
.filter-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }}
.filter-btn {{ padding: 4px 12px; border-radius: 16px; border: 1px solid var(--border);
               background: var(--surface); color: var(--text2); cursor: pointer;
               font-size: 0.78rem; transition: all 0.15s; }}
.filter-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}

.subtitle {{ color: var(--text2); font-size: 0.88rem; margin-bottom: 16px; }}
.note {{ background: var(--surface); border-left: 3px solid var(--accent);
         padding: 10px 14px; margin: 12px 0; font-size: 0.82rem; color: var(--text2);
         border-radius: 0 var(--radius) var(--radius) 0; }}

/* Responsive */
@media (max-width: 640px) {{
    .metrics {{ grid-template-columns: repeat(2, 1fr); }}
    .mech-grid {{ grid-template-columns: 1fr; }}
    table {{ font-size: 0.78rem; }}
    td, th {{ padding: 6px 8px; }}
    .hide-mobile {{ display: none; }}
}}

/* Search */
.search-box {{ width: 100%; padding: 8px 12px; border-radius: var(--radius);
               border: 1px solid var(--border); background: var(--surface);
               color: var(--text); font-size: 0.85rem; margin-bottom: 12px; }}
.search-box::placeholder {{ color: var(--text2); }}
</style>
</head>
<body>
<h1>Site Intelligence Report</h1>
<p class="subtitle">Sweepstakes automation analysis — {s["active_sites"]} active sites across {s["multi_site_families"]} platform families.<br>
Built from the Casino Masterlist spreadsheet (updated 2026-09-21).</p>

<div class="metrics">
    <div class="metric">
        <div class="val">{s["active_sites"]}</div>
        <div class="lbl">Active Sites</div>
    </div>
    <div class="metric">
        <div class="val">{s["multi_site_families"]}</div>
        <div class="lbl">Platform Families</div>
    </div>
    <div class="metric">
        <div class="val">{s["sites_in_families"]}</div>
        <div class="lbl">Sites in Families</div>
    </div>
    <div class="metric highlight">
        <div class="val">{s["adapters_saved"]}</div>
        <div class="lbl">Adapters Saved</div>
    </div>
    <div class="metric">
        <div class="val">{s["unique_adapters"]}</div>
        <div class="lbl">Unique Adapters</div>
    </div>
    <div class="metric">
        <div class="val">${r["daily_expected"]:.0f}</div>
        <div class="lbl">Est. Daily / ${r["monthly_expected"]:.0f} mo</div>
    </div>
</div>

<div class="note">
    <strong>The key finding:</strong> {s["multi_site_families"]} parent companies operate {s["sites_in_families"]} of the {s["active_sites"]} active sites.
    Sites sharing a parent company share the same backend, the same SPA shell, and the same daily-bonus flow.
    One adapter per family, not per URL — that's <strong>{s["adapters_saved"]} adapters nobody needs to build or maintain</strong>.
</div>

<!-- ============================================ PLATFORM FAMILIES -->
<h2>&#128279; Platform Family Map</h2>
<p>Sites sharing a parent company share an adapter. One selector fix repairs every site on that platform.</p>
<table id="familyTable">
<thead><tr>
    <th onclick="sortTable('familyTable',0)">Parent Company</th>
    <th onclick="sortTable('familyTable',1)">Sites</th>
    <th>Site Names</th>
    <th>Mechanisms</th>
    <th onclick="sortTable('familyTable',4)">Daily Range</th>
    <th onclick="sortTable('familyTable',5)">Saved</th>
</tr></thead>
<tbody>{fam_rows}</tbody>
</table>

<!-- ============================================ MECHANISM TAXONOMY -->
<h2>&#9881; Bonus Mechanism Taxonomy</h2>
<p>Every site's daily bonus falls into one of these claim patterns. The adapter's <code>claim_daily()</code> method handles the pattern, not the site.</p>
<div class="mech-grid">{mech_cards}</div>

<!-- ============================================ ARCHITECTURE -->
<h2>&#128736; Architecture Blueprint</h2>
<div class="arch-box">
<svg class="arch-svg" viewBox="0 0 900 420" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="900" height="420" fill="none"/>

  <!-- Scheduler -->
  <rect x="20" y="20" width="160" height="60" rx="8" fill="#1a2233" stroke="#30363d"/>
  <text x="100" y="45" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="700">SCHEDULER</text>
  <text x="100" y="62" text-anchor="middle" fill="#8b949e" font-size="9">Cron + interval engine</text>

  <!-- Orchestrator -->
  <rect x="220" y="20" width="160" height="60" rx="8" fill="#1a2233" stroke="#58a6ff" stroke-width="2"/>
  <text x="300" y="45" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="700">ORCHESTRATOR</text>
  <text x="300" y="62" text-anchor="middle" fill="#8b949e" font-size="9">Picks adapter, runs claim</text>

  <!-- Arrow: scheduler -> orchestrator -->
  <line x1="180" y1="50" x2="218" y2="50" stroke="#58a6ff" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Anti-detection -->
  <rect x="420" y="20" width="160" height="60" rx="8" fill="#1a2233" stroke="#d29922"/>
  <text x="500" y="45" text-anchor="middle" fill="#d29922" font-size="12" font-weight="700">ANTI-DETECTION</text>
  <text x="500" y="62" text-anchor="middle" fill="#8b949e" font-size="9">Fingerprint + proxy per site</text>

  <!-- Arrow: orchestrator -> anti-detection -->
  <line x1="380" y1="50" x2="418" y2="50" stroke="#d29922" stroke-width="1.5" marker-end="url(#arrow2)"/>

  <!-- Browser Pool -->
  <rect x="620" y="20" width="160" height="60" rx="8" fill="#1a2233" stroke="#30363d"/>
  <text x="700" y="45" text-anchor="middle" fill="#bc8cff" font-size="12" font-weight="700">BROWSER POOL</text>
  <text x="700" y="62" text-anchor="middle" fill="#8b949e" font-size="9">Playwright contexts</text>

  <!-- Arrow: anti-detect -> browser -->
  <line x1="580" y1="50" x2="618" y2="50" stroke="#bc8cff" stroke-width="1.5" marker-end="url(#arrow3)"/>

  <!-- Adapter layer -->
  <rect x="60" y="120" width="780" height="170" rx="8" fill="#0d1117" stroke="#30363d" stroke-dasharray="5,5"/>
  <text x="450" y="145" text-anchor="middle" fill="#8b949e" font-size="11" font-weight="600">ADAPTER LAYER — one class per platform family</text>

  <!-- Adapter boxes -->
  <rect x="90" y="160" width="120" height="55" rx="6" fill="#1a2233" stroke="#3fb950"/>
  <text x="150" y="182" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">B2Adapter</text>
  <text x="150" y="200" text-anchor="middle" fill="#8b949e" font-size="8">6 sites</text>

  <rect x="230" y="160" width="120" height="55" rx="6" fill="#1a2233" stroke="#3fb950"/>
  <text x="290" y="182" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">VGWAdapter</text>
  <text x="290" y="200" text-anchor="middle" fill="#8b949e" font-size="8">4 sites</text>

  <rect x="370" y="160" width="120" height="55" rx="6" fill="#1a2233" stroke="#3fb950"/>
  <text x="430" y="182" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">BlazesoftAdapter</text>
  <text x="430" y="200" text-anchor="middle" fill="#8b949e" font-size="8">4 sites</text>

  <rect x="510" y="160" width="120" height="55" rx="6" fill="#1a2233" stroke="#3fb950"/>
  <text x="570" y="182" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600">FuncraftersAdapter</text>
  <text x="570" y="200" text-anchor="middle" fill="#8b949e" font-size="8">4 sites</text>

  <rect x="650" y="160" width="120" height="55" rx="6" fill="#1a2233" stroke="#58a6ff"/>
  <text x="710" y="182" text-anchor="middle" fill="#58a6ff" font-size="10" font-weight="600">+ {s["unique_adapters"] - 4} more</text>
  <text x="710" y="200" text-anchor="middle" fill="#8b949e" font-size="8">1 per platform</text>

  <!-- Site names under adapters -->
  <text x="150" y="240" text-anchor="middle" fill="#8b949e" font-size="7">McLuck, Playfame, Hello Millions</text>
  <text x="150" y="250" text-anchor="middle" fill="#8b949e" font-size="7">Jackpota, SpinBlitz, MegaBonanza</text>

  <text x="290" y="240" text-anchor="middle" fill="#8b949e" font-size="7">Chumba, LuckyLandSlots</text>
  <text x="290" y="250" text-anchor="middle" fill="#8b949e" font-size="7">LuckyLandCasino, Global Poker</text>

  <text x="430" y="240" text-anchor="middle" fill="#8b949e" font-size="7">Sportzino, Zula</text>
  <text x="430" y="250" text-anchor="middle" fill="#8b949e" font-size="7">YayCasino, Fortune Coins</text>

  <text x="570" y="240" text-anchor="middle" fill="#8b949e" font-size="7">RichSweeps, SweepsRoyal</text>
  <text x="570" y="250" text-anchor="middle" fill="#8b949e" font-size="7">SpeedSweeps, DimeSweeps</text>

  <!-- Data layer -->
  <rect x="60" y="310" width="250" height="55" rx="8" fill="#1a2233" stroke="#30363d"/>
  <text x="185" y="335" text-anchor="middle" fill="#58a6ff" font-size="11" font-weight="600">CREDENTIAL VAULT</text>
  <text x="185" y="352" text-anchor="middle" fill="#8b949e" font-size="9">Encrypted at rest, per-site injection</text>

  <rect x="330" y="310" width="250" height="55" rx="8" fill="#1a2233" stroke="#30363d"/>
  <text x="455" y="335" text-anchor="middle" fill="#58a6ff" font-size="11" font-weight="600">RESULTS DB</text>
  <text x="455" y="352" text-anchor="middle" fill="#8b949e" font-size="9">Claims, balances, errors, streaks</text>

  <rect x="600" y="310" width="250" height="55" rx="8" fill="#1a2233" stroke="#30363d"/>
  <text x="725" y="335" text-anchor="middle" fill="#58a6ff" font-size="11" font-weight="600">DASHBOARD + ALERTS</text>
  <text x="725" y="352" text-anchor="middle" fill="#8b949e" font-size="9">Telegram / Discord / Web UI</text>

  <!-- Arrows down from orchestrator -->
  <line x1="300" y1="80" x2="300" y2="118" stroke="#58a6ff" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="185" y1="290" x2="185" y2="308" stroke="#30363d" stroke-width="1"/>
  <line x1="455" y1="290" x2="455" y2="308" stroke="#30363d" stroke-width="1"/>
  <line x1="725" y1="290" x2="725" y2="308" stroke="#30363d" stroke-width="1"/>

  <!-- Config box -->
  <rect x="20" y="390" width="860" height="25" rx="4" fill="#1a2233" stroke="#30363d"/>
  <text x="450" y="407" text-anchor="middle" fill="#8b949e" font-size="9">config.json — sites, selectors, credentials refs, schedule — everything outside the code, reloaded every cycle</text>

  <!-- Arrow markers -->
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6" fill="#58a6ff"/>
    </marker>
    <marker id="arrow2" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6" fill="#d29922"/>
    </marker>
    <marker id="arrow3" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6" fill="#bc8cff"/>
    </marker>
  </defs>
</svg>
</div>

<div class="note">
    <strong>Why this shape:</strong> The orchestrator picks the adapter by <code>config.sites[n].adapter</code> — it never knows which site it's talking to.
    Adding a new site on an existing platform means adding a config block (URL + selectors), not writing code.
    A broken selector fix propagates to every site on that platform automatically.
</div>

<!-- ============================================ SITE HEALTH -->
<h2>&#9888; Site Health Matrix</h2>
<p>{len(health["healthy"])} healthy, {len(health["risky"])} at risk, {len(health["dead"])} dead. At-risk sites have reported issues:</p>
<table>
<thead><tr><th>Site</th><th>Issue</th></tr></thead>
<tbody>{risk_rows}</tbody>
</table>
<p style="margin-top:8px;"><strong>Dead / sunsetted:</strong> {dead_list}</p>

<!-- ============================================ REVENUE -->
<h2>&#128176; Revenue Projection by Tier</h2>
<table>
<thead><tr><th>Tier</th><th>Sites</th><th>Daily (est.)</th><th>Monthly (est.)</th></tr></thead>
<tbody>{rev_rows}
<tr style="font-weight:700; border-top:2px solid var(--border)">
    <td>Total</td><td>{r["active_sites"]}</td>
    <td>${r["daily_expected"]:.2f}</td><td>${r["monthly_expected"]:.2f}</td>
</tr></tbody>
</table>
<div class="note">
    Expected value = 70% × min + 30% × max. Wheel spins typically land near the floor.
    The spreadsheet's own estimate ($1,407/mo) likely uses more conservative assumptions per-site.
</div>

<!-- ============================================ ALL SITES -->
<h2>&#128200; Full Site Directory</h2>
<input type="text" class="search-box" id="siteSearch" placeholder="Search sites..." oninput="filterSites()">
<div class="filter-row">
    <button class="filter-btn active" onclick="filterTier('all')">All ({s["active_sites"]})</button>
    <button class="filter-btn" onclick="filterTier('god')">God ({r["by_tier"]["god"]["count"]})</button>
    <button class="filter-btn" onclick="filterTier('high')">High ({r["by_tier"]["high"]["count"]})</button>
    <button class="filter-btn" onclick="filterTier('medium')">Medium ({r["by_tier"]["medium"]["count"]})</button>
    <button class="filter-btn" onclick="filterTier('trash')">Trash ({r["by_tier"]["trash"]["count"]})</button>
</div>
<table id="siteTable">
<thead><tr>
    <th onclick="sortTable('siteTable',0)">Site</th>
    <th>Tier</th>
    <th onclick="sortTable('siteTable',2)" class="hide-mobile">Parent Company</th>
    <th>Mechanism</th>
    <th onclick="sortTable('siteTable',4)">Daily</th>
    <th onclick="sortTable('siteTable',5)">Min Redeem</th>
    <th onclick="sortTable('siteTable',6)">Difficulty</th>
</tr></thead>
<tbody>{all_rows}</tbody>
</table>

<!-- ============================================ CODE -->
<h2>&#128230; Downloadable Files</h2>
<div class="code-section">
    <div class="code-header">
        <span>adapter_interface.py</span>
        <button onclick="downloadFile('adapter_interface.py', adapterCode)">Download</button>
    </div>
    <pre id="adapterPre">{_escape(adapter_code[:3000])}{"..." if len(adapter_code) > 3000 else ""}</pre>
</div>
<div class="code-section">
    <div class="code-header">
        <span>config.example.json</span>
        <button onclick="downloadFile('config.example.json', configCode)">Download</button>
    </div>
    <pre id="configPre">{_escape(config_code[:2500])}{"..." if len(config_code) > 2500 else ""}</pre>
</div>

<!-- ============================================ LIMITS -->
<h2>&#9888; Limits of This Analysis</h2>
<ul style="padding-left:20px; margin: 8px 0;">
    <li><strong>Parent company grouping is from the spreadsheet, not from live site inspection.</strong>
    Some "standalone" companies may share a white-label platform — the real adapter count could be lower.
    The first week of development will discover these by comparing DOM structures.</li>
    <li><strong>Difficulty scores are estimated</strong> from mechanism type and parent company reputation.
    Actual anti-bot posture (Cloudflare Turnstile, DataDome, PerimeterX) needs live probing.</li>
    <li><strong>Revenue assumes all bonuses are claimable.</strong> Some sites require a purchase first (WOW Vegas),
    and some have reduced bonuses after initial period (LuckyBitsVegas, Rolla).</li>
    <li><strong>The adapter interface is a contract, not production code.</strong> The B2Adapter example shows
    the pattern; real selectors come from inspecting the live sites during development.</li>
</ul>

<p style="margin-top: 24px; color: var(--text2); font-size: 0.8rem;">
    Analysis generated from spreadsheet data. No live site scraping was performed.
    Parent companies, restricted states, and bonus amounts are as reported in the source document.<br>
    — Sebastian
</p>

<script>
const adapterCode = {json.dumps(adapter_code)};
const configCode = {json.dumps(config_code)};

function downloadFile(name, content) {{
    const blob = new Blob([content], {{type: 'text/plain'}});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
}}

let currentTier = 'all';
function filterTier(tier) {{
    currentTier = tier;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    filterSites();
}}

function filterSites() {{
    const query = document.getElementById('siteSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#siteTable tbody tr');
    rows.forEach(row => {{
        const name = row.cells[0].textContent.toLowerCase();
        const parent = row.cells[2] ? row.cells[2].textContent.toLowerCase() : '';
        const matchesSearch = name.includes(query) || parent.includes(query);
        const tierClass = row.className;
        const matchesTier = currentTier === 'all' || tierClass.includes('tier-' + currentTier);
        row.style.display = matchesSearch && matchesTier ? '' : 'none';
    }});
}}

function sortTable(tableId, col) {{
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const dir = table.dataset.sortDir === 'asc' ? 'desc' : 'asc';
    table.dataset.sortDir = dir;
    rows.sort((a, b) => {{
        let va = a.cells[col]?.textContent.trim() || '';
        let vb = b.cells[col]?.textContent.trim() || '';
        const na = parseFloat(va.replace(/[^0-9.-]/g, ''));
        const nb = parseFloat(vb.replace(/[^0-9.-]/g, ''));
        if (!isNaN(na) && !isNaN(nb)) {{
            return dir === 'asc' ? na - nb : nb - na;
        }}
        return dir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    }});
    rows.forEach(r => tbody.appendChild(r));
}}
</script>
</body>
</html>'''

    return html


def _adapter_hint(m):
    hints = {
        CLICK:  "Navigate to bonus URL → <code>page.click(claim_selector)</code> → read result",
        WHEEL:  "Navigate → <code>page.click(spin_selector)</code> → wait for animation → parse outcome element",
        STREAK: "Navigate → check streak day indicator → <code>page.click(claim_selector)</code> → track day count for reset detection",
        TIMED:  "Run every N hours → check cooldown timer → claim if ready → schedule next run from timer value",
        MULTI:  "Navigate to coin store → click daily tab → <code>page.click(claim_selector)</code> → close modal",
        LOCKED: "Check purchase status first → skip if no active package → claim if unlocked",
        VIP:    "Check VIP level badge → skip if below threshold → claim if eligible",
    }
    return hints.get(m, "Site-specific flow")


def _escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    results = run_analysis()
    html = render(results)
    out_dir = os.path.join(os.path.dirname(__file__), "..", "site")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Generated {out_path} ({len(html)} bytes)")

    # Also save analysis JSON
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "analysis.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("Saved data/analysis.json")
