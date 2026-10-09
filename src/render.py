"""
Sweeps Intelligence: white, tabbed dashboard.
Reads the analysis (analyze.py) and the site database (data.py) and writes a
single self-contained index.html that can be deployed as-is (Vercel, Netlify,
any static host).
"""

import json
import os
import statistics
import sys
from html import escape as e

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import run_analysis, expected_daily, eff_max, DAILY_CAP  # noqa: E402
from data import (  # noqa: E402
    SITES, GOD, HIGH, MED, TRASH, DEAD,
    CLICK, WHEEL, STREAK, TIMED, MULTI, LOCKED, VIP,
)

AUTHOR = "Santiago"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TIER_LABEL = {GOD: "God", HIGH: "High", MED: "Medium", TRASH: "Trash", DEAD: "Dead"}
TIER_ORDER = [GOD, HIGH, MED, TRASH]

# ---------------------------------------------------------------------------
# Copy for each claim type: plain-language line plus what the bot actually does
# ---------------------------------------------------------------------------
MECH = {
    CLICK: dict(
        label="One-button claim",
        plain="One button. The bot presses it and the coins arrive.",
        tech="Open bonus page, <code>click(claim)</code>, read amount, read balance.",
        key="click",
    ),
    WHEEL: dict(
        label="Spin wheel",
        plain="A wheel spins and lands on a random amount. The bot has to wait for the animation to stop before it reads the prize.",
        tech="<code>click(spin)</code>, wait for the result element to settle, parse amount. Never read mid-animation.",
        key="wheel",
    ),
    STREAK: dict(
        label="Streak calendar",
        plain="The reward grows with each consecutive day and resets if a day is missed, so the bot must never skip a day and must warn you if it does.",
        tech="Read the streak-day indicator, claim, store the day count. Alert on a reset or a missed day.",
        key="streak",
    ),
    TIMED: dict(
        label="Timed interval",
        plain="The bonus can be claimed several times a day. The bot reads the countdown and schedules its own next visit.",
        tech="Read cooldown timer, claim if ready, enqueue the next run at timer end. Runs on an interval job, not the daily window.",
        key="timed",
    ),
    MULTI: dict(
        label="Multi-step menu",
        plain="The daily bonus sits behind a couple of menu clicks, for example the coin store and then a daily tab.",
        tech="Navigate coin store, open daily tab, <code>click(claim)</code>, close modal. Selectors come from config.",
        key="multi",
    ),
    LOCKED: dict(
        label="Purchase-locked",
        plain="The daily bonus only works after buying a coin package. The bot detects this, skips the site and tells you.",
        tech="Check package status first. Return <code>purchase_req</code> and skip. No retry.",
        key="locked",
    ),
    VIP: dict(
        label="VIP-locked",
        plain="The daily bonus needs a VIP tier. The bot detects this, skips the site and tells you.",
        tech="Check VIP badge. Return <code>vip_required</code> and skip. No retry.",
        key="vip",
    ),
}
MECH_ORDER = [CLICK, WHEEL, STREAK, MULTI, TIMED, LOCKED, VIP]

# Outcomes the adapter can return (mirrors ClaimResult in adapter_interface.py)
OUTCOMES = [
    ("success · wheel_spun · streak_day", "Bonus claimed.", "Store the amount and the new balance."),
    ("already_claimed", "Already collected today.", "Log it and move on. Normal after a retry."),
    ("purchase_req · vip_required", "Locked behind a purchase or VIP level.", "Mark the site as locked and skip it. No retry."),
    ("site_down", "Site unreachable or in maintenance.", "Retry at 5, 15 and 60 minutes, then alert."),
    ("login_failed", "Password rejected, or a 2FA / phone-code prompt appeared.", "Stop at once and alert. Repeated attempts risk a lockout."),
    ("captcha", "A CAPTCHA appeared.", "Send it to a solving service. Alert if it stays unsolved."),
    ("ui_changed", "An expected button or field was not found.", "Save a screenshot, alert, and pause that platform. One selector fix repairs every site on it."),
    ("error", "Anything unexpected.", "Retry, then alert with the error and a screenshot."),
]


def money(x):
    return f"${x:,.2f}"


def tier_badge(t):
    return f'<span class="badge t-{t}">{TIER_LABEL[t]}</span>'


def sq(site):
    return f'<i class="sq t-{site["tier"]}" title="{e(site["name"])} · {TIER_LABEL[site["tier"]]}"></i>'


def diff_cell(d):
    cls = "d-easy" if d <= 2.5 else "d-mid" if d <= 3.5 else "d-hard"
    pct = int(d / 5 * 100)
    return (f'<span class="diff {cls}"><span class="diff-track"><i style="width:{pct}%"></i></span>'
            f'<b>{d:.1f}</b></span>')


def bar_row(label, value_text, frac, color_var, sub=""):
    return (f'<div class="bar-row"><div class="bar-label">{label}{f"<small>{sub}</small>" if sub else ""}</div>'
            f'<div class="bar-track"><i style="width:{max(frac, 0.015) * 100:.1f}%;background:var({color_var})"></i></div>'
            f'<div class="bar-val">{value_text}</div></div>')


def pair(plain, tech):
    return (f'<div class="pair"><div class="plain"><span class="tag">In plain English</span><p>{plain}</p></div>'
            f'<div class="tech"><span class="tag">Technical</span><p>{tech}</p></div></div>')


# ---------------------------------------------------------------------------
# Architecture diagram (drawn on one 1000 x 540 grid, colours from CSS tokens)
# ---------------------------------------------------------------------------
def node(x, y, w, h, title, l1, l2=None, step=None, cls="node"):
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
    out += f'<text class="s-title" x="{x + 16}" y="{y + 29}">{title}</text>'
    out += f'<text class="s-sub" x="{x + 16}" y="{y + 49}">{l1}</text>'
    if l2:
        out += f'<text class="s-sub" x="{x + 16}" y="{y + 65}">{l2}</text>'
    if step:
        out += (f'<circle class="s-badge" cx="{x + w - 22}" cy="{y + 22}" r="11"/>'
                f'<text class="s-step" x="{x + w - 22}" y="{y + 26}" text-anchor="middle">{step}</text>')
    return out


def arrow(x1, y1, x2, y2):
    return f'<path class="s-arrow" d="M{x1} {y1} L{x2} {y2}" marker-end="url(#ah)"/>'


def architecture_svg(results):
    fams = [f for f in results["families"] if f["count"] > 1]
    top = fams[:5]
    rest_fams = len(fams) - len(top)
    singles = results["summary"]["unique_adapters"] - len(fams)
    more = results["summary"]["unique_adapters"] - len(top)

    s = ['<svg class="arch" viewBox="0 0 1000 540" role="img" '
         'aria-label="Architecture: scheduler, orchestrator, session factory and browser pool feed an adapter layer, '
         'which writes to a results database and alerts.">',
         '<defs><marker id="ah" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto">'
         '<path d="M0 0 L9 4 L0 8 Z" class="s-head"/></marker></defs>']

    # Top row
    s.append(node(30, 24, 190, 84, "Scheduler", "Cron + interval engine", "Staggered 45 s apart", "1"))
    s.append(node(280, 24, 190, 84, "Orchestrator", "Picks adapter per site", "Retries 5 / 15 / 60 min", "2"))
    s.append(node(530, 24, 190, 84, "Session factory", "Fingerprint · proxy · vault", "Same “device” each day", "3"))
    s.append(node(780, 24, 190, 84, "Browser pool", "Playwright contexts", "One saved profile per site", "4"))
    for x1, x2 in ((220, 278), (470, 528), (720, 778)):
        s.append(arrow(x1, 66, x2, 66))

    # Adapter layer
    s.append('<rect class="layer" x="30" y="156" width="940" height="196" rx="12"/>')
    s.append('<text class="s-layer" x="52" y="184">ADAPTER LAYER · one class per platform family</text>')
    s.append('<circle class="s-badge" cx="948" cy="178" r="11"/><text class="s-step" x="948" y="182" text-anchor="middle">5</text>')
    s.append(arrow(875, 108, 875, 154))
    cx = 39
    for f in top:
        name = {"WW Funcrafters JWA LLC": "Funcrafters", "SWPMTECH LTD": "SWPM"}.get(f["parent"], f["parent"])
        sites = f["sites"]
        s.append(f'<rect class="card" x="{cx}" y="204" width="142" height="122" rx="8"/>')
        s.append(f'<text class="s-title" x="{cx + 12}" y="232">{e(name)}</text>')
        s.append(f'<text class="s-count" x="{cx + 12}" y="252">{f["count"]} sites</text>')
        s.append(f'<text class="s-tiny" x="{cx + 12}" y="276">{e(sites[0])}</text>')
        s.append(f'<text class="s-tiny" x="{cx + 12}" y="291">{e(sites[1])}</text>')
        s.append(f'<text class="s-tiny" x="{cx + 12}" y="306">+ {len(sites) - 2} more</text>')
        cx += 156
    s.append(f'<rect class="card more" x="{cx}" y="204" width="142" height="122" rx="8"/>')
    s.append(f'<text class="s-title" x="{cx + 12}" y="232">+ {more} more</text>')
    s.append(f'<text class="s-count" x="{cx + 12}" y="252">adapters</text>')
    s.append(f'<text class="s-tiny" x="{cx + 12}" y="276">{rest_fams} more families</text>')
    s.append(f'<text class="s-tiny" x="{cx + 12}" y="291">{singles} single-site</text>')
    s.append(f'<text class="s-tiny" x="{cx + 12}" y="306">platforms</text>')

    # Bottom row
    s.append(arrow(500, 352, 500, 392))
    s.append(node(30, 394, 290, 70, "Credential vault", "Encrypted at rest", None, None, "node soft"))
    s.append(f'<text class="s-tiny" x="{30 + 16}" y="{394 + 62}">read by step 3, per site, at run time</text>')
    s.append(node(355, 394, 290, 70, "Results database", "Claims, balances, streaks", None, "6"))
    s.append(node(680, 394, 290, 70, "Alerts + dashboard", "Telegram · Discord · web", None, "7"))
    s.append(arrow(645, 429, 678, 429))

    # Config strip
    s.append('<rect class="strip" x="30" y="490" width="940" height="34" rx="8"/>')
    s.append('<text class="s-sub" x="500" y="512" text-anchor="middle">config.json holds sites, selectors, schedule and credential keys. '
             'It is reloaded every cycle, so changes need no redeploy.</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------
def build_context(results):
    active = [s for s in SITES if s["tier"] != DEAD]
    multi = [f for f in results["families"] if f["count"] > 1]
    multi_names = {f["parent"] for f in multi}
    singles = [s for s in active if s["parent"] not in multi_names]
    days = [s["min_redeem"] / expected_daily(s) for s in active if expected_daily(s) > 0]
    diffs = {d["name"]: d["difficulty"] for d in results["difficulties"]}
    click_n = len(results["mechanisms"].get(CLICK, {}).get("sites", []))
    return dict(active=active, multi=multi, singles=singles, days=days, diffs=diffs,
                median_days=round(statistics.median(days)), click_n=click_n)


def panel_overview(r, c):
    s, rev = r["summary"], r["revenue"]
    steps = [
        ("Wake up", "A scheduler starts each site’s turn, 45 seconds apart, so traffic looks like a person and not a burst.",
         "cron window 06:00–23:00 ET plus interval jobs for timed sites"),
        ("Sign in", "Each site gets its own saved browser identity and an internet address in a state where the site operates.",
         "Playwright persistent context, fingerprint profile, sticky residential proxy, vault credentials"),
        ("Claim", "The program for that platform presses the right buttons for that kind of bonus and reads what it got.",
         "<code>adapter.claim_daily()</code> returns a <code>ClaimOutcome</code>"),
        ("Report", "Every result is logged. You get a message only when something needs a human.",
         "results DB, plus Telegram or Discord alerts on UI change, ban signal, balance at redemption"),
    ]
    steps_html = "".join(
        f'<li><span class="step-n">{i + 1}</span><h4>{t}</h4><p>{p}</p><code class="line">{tech}</code></li>'
        for i, (t, p, tech) in enumerate(steps))

    tier_max = max(v["daily_expected"] for v in rev["by_tier"].values())
    tier_rows = ""
    for t in TIER_ORDER:
        v = rev["by_tier"][t]
        per_site = v["daily_expected"] / v["count"] if v["count"] else 0
        tier_rows += bar_row(tier_badge(t), money(v["daily_expected"]) + " / day", v["daily_expected"] / tier_max,
                             f"--tf-{t}", f'{v["count"]} sites · {money(per_site)} per site')

    capped = ", ".join(rev["capped_sites"])
    return f'''
<section class="sec first">
  <h2>What the bot does each day</h2>
  <ol class="steps4">{steps_html}</ol>
</section>

<section class="sec">
  {pair("Most of this job is repeating the same few moves on many sites. The plan is to write one program per platform instead of one per website, and to keep everything that differs between sites in a settings file.",
        "One <code>SiteAdapter</code> subclass per platform family. URL, selectors and credential key live in <code>config.json</code>. Adding a site is one JSON block. Fixing a broken selector on a platform repairs every site on it.")}
</section>

<section class="sec">
  <h2>What the masterlist tells us</h2>
  <div class="finds">
    <div><b>{s["adapters_saved"]}<small> adapters saved</small></b>
      <p>{s["multi_site_families"]} parent companies run {s["sites_in_families"]} sites. Those {s["sites_in_families"]} sites need {s["multi_site_families"]} adapters instead of {s["sites_in_families"]}, which removes {s["adapters_saved"]} from the build.</p></div>
    <div><b>{c["click_n"]}<small> of {s["active_sites"]}</small></b>
      <p>sites are a single button press ({round(c["click_n"] / s["active_sites"] * 100)}%). This is the easy majority and gets built first.</p></div>
    <div><b>{c["median_days"]}<small> days</small></b>
      <p>is the median time for one site to reach its minimum redemption at the expected daily rate. Payouts are slow, so balance tracking matters more than speed.</p></div>
  </div>
</section>

<section class="sec">
  <h2>Expected daily yield</h2>
  <p class="lede">Tier is the masterlist’s own rating of each site. Figures are dollars per day as listed in the masterlist, where 1 SC redeems for about $1.</p>
  <div class="bars">{tier_rows}</div>
  <div class="range">
    <div><span>Floor</span><b>{money(rev["daily_min"])}</b><small>every site pays its minimum</small></div>
    <div class="mid"><span>Expected</span><b>{money(rev["daily_expected"])}</b><small>about {money(rev["monthly_expected"])} a month</small></div>
    <div><span>Ceiling</span><b>{money(rev["daily_max"])}</b><small>every site pays its maximum</small></div>
  </div>
  <p class="note">Method: expected = 70% of each site’s minimum plus 30% of its maximum. Each maximum is capped at {money(DAILY_CAP)} per site per day.
  Eight sites list higher numbers ({e(capped)}). Those come from purchase packs or jackpot-wheel prizes, not the standard daily claim.</p>
</section>
'''


def panel_families(r, c):
    s = r["summary"]
    cards = ""
    for f in c["multi"]:
        by_name = {x["name"]: x for x in SITES}
        squares = "".join(sq(by_name[n]) for n in f["sites"])
        cards += (f'<div class="fam"><div class="fam-head"><b>{e(f["parent"])}</b>'
                  f'<span>{f["count"]} sites → 1 adapter</span></div>'
                  f'<div class="sqs">{squares}</div>'
                  f'<p class="fam-sites">{e(" · ".join(f["sites"]))}</p></div>')
    single_sq = "".join(sq(x) for x in c["singles"])
    cards += (f'<div class="fam wide"><div class="fam-head"><b>Independent platforms</b>'
              f'<span>{len(c["singles"])} sites → {len(c["singles"])} adapters</span></div>'
              f'<div class="sqs">{single_sq}</div>'
              f'<p class="fam-sites">No other site in the list shares their parent company, so each needs its own adapter.</p></div>')

    rows = ""
    for f in c["multi"]:
        mech_tags = " ".join(f'<span class="mtag m-{MECH[m]["key"]}">{MECH[m]["label"]}</span>' for m in f["mechanisms"] if m in MECH)
        rows += (f'<tr><td data-v="{e(f["parent"])}"><b>{e(f["parent"])}</b></td>'
                 f'<td data-v="{f["count"]}" class="num">{f["count"]}</td>'
                 f'<td class="muted">{e(", ".join(f["sites"]))}</td>'
                 f'<td>{mech_tags}</td>'
                 f'<td data-v="{f["daily_max"]}" class="num">{money(f["daily_min"])} – {money(f["daily_max"])}</td>'
                 f'<td data-v="{f["adapters_saved"]}" class="num good">{f["adapters_saved"]}</td></tr>')

    return f'''
<section class="sec first">
  <h2>{s["active_sites"]} sites run on {s["unique_adapters"]} platforms</h2>
  {pair("Many casino sites with different names are run by the same company on the same software. One program can drive all of them, so a repair made once fixes every site in the group.",
        "Grouping by parent company from the masterlist gives " + str(s["multi_site_families"]) + " families covering " + str(s["sites_in_families"]) + " sites. Each family gets one adapter class. Inside a family the claim flow can still differ (VGW mixes click, streak and multi-step), so the adapter takes per-site flow overrides from config.")}
</section>

<section class="sec">
  <div class="legend"><span><i class="sq t-god"></i>God</span><span><i class="sq t-high"></i>High</span><span><i class="sq t-medium"></i>Medium</span><span><i class="sq t-trash"></i>Trash</span><span class="muted">Each square is one site.</span></div>
  <div class="fams">{cards}</div>
</section>

<section class="sec">
  <h2>Family details</h2>
  <div class="tbl-wrap"><table class="sortable">
    <thead><tr><th>Parent company</th><th class="num">Sites</th><th>Sites in the family</th><th>Claim types</th><th class="num">Daily range</th><th class="num">Adapters saved</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
  <p class="note">To verify in week 1: a shared parent company is taken to mean a shared platform. The first step of the build compares page structure across each family to confirm it, and splits a family if it turns out to be two platforms.</p>
</section>
'''


def panel_claims(r, c):
    mechs = r["mechanisms"]
    total = sum(len(v["sites"]) for v in mechs.values())
    seg, legend, cards = "", "", ""
    for m in MECH_ORDER:
        if m not in mechs:
            continue
        info, n = MECH[m], len(mechs[m]["sites"])
        pct = n / total * 100
        seg += f'<i class="m-{info["key"]}" style="width:{pct:.2f}%" title="{info["label"]}: {n}"></i>'
        legend += f'<span><i class="dot m-{info["key"]}"></i>{info["label"]} <b>{n}</b></span>'
        names = mechs[m]["sites"]
        shown = ", ".join(names[:6]) + (f" and {len(names) - 6} more" if len(names) > 6 else "")
        cards += (f'<article class="mcard"><div class="mhead"><i class="dot m-{info["key"]}"></i><h3>{info["label"]}</h3>'
                  f'<span class="mcount">{n} site{"s" if n != 1 else ""} · {pct:.0f}%</span></div>'
                  f'<p>{info["plain"]}</p><p class="mtech"><span class="tag">Bot behaviour</span>{info["tech"]}</p>'
                  f'<p class="msites">{e(shown)}</p></article>')
    return f'''
<section class="sec first">
  <h2>Seven ways a site hands out its daily bonus</h2>
  {pair("Every site fits one of seven patterns. The bot is built around the pattern, not the website, which is why a handful of building blocks can cover all " + str(total) + " sites.",
        "<code>claim_daily()</code> in each adapter implements one of these flows. The flow is chosen by <code>daily_type</code> in the site’s config block, so a site that changes its bonus style only needs a config edit.")}
</section>

<section class="sec">
  <div class="stack" role="img" aria-label="Share of sites by claim type">{seg}</div>
  <div class="legend spread">{legend}</div>
  <div class="mgrid">{cards}</div>
</section>
'''


def panel_architecture(r, c):
    steps = [
        ("Scheduler", "Wakes up each site’s turn.",
         "cron window 06:00–23:00 ET. Sites are staggered 45 s apart, so a full pass over 95 sites takes about 71 minutes. Timed sites run on their own interval."),
        ("Orchestrator", "Looks up the site and picks the program for its platform.",
         "Reads <code>config.json</code> for the adapter class and selectors. Retries 3 times at 5, 15 and 60 minutes."),
        ("Session factory", "Prepares a believable visitor: a saved browser identity and an internet address in an allowed state.",
         "Fingerprint profile (canvas, WebGL, audio, fonts) stable per site. Sticky residential proxy per run. Credentials decrypted at run time only."),
        ("Browser pool", "Opens the site as that visitor and restores yesterday’s login.",
         "Playwright persistent context. Cookies restored first, fresh login only if the session expired."),
        ("Adapter", "Finds the daily bonus, checks whether it can be claimed, claims it and reads the amount and balance.",
         "<code>adapter.claim_daily()</code> returns <code>ClaimOutcome(result, value_sc, balance, screenshot)</code>."),
        ("Results database", "Records what happened.",
         "Append-only claims table, streak counters, balance history per site."),
        ("Alerts", "Tells you only when something needs a human.",
         "Telegram or Discord on <code>ui_changed</code>, <code>login_failed</code>, a ban signal, or a balance reaching the minimum redemption."),
    ]
    steps_html = "".join(
        f'<li><span class="step-n">{i + 1}</span><div><h4>{t}</h4><p>{p}</p><code class="line">{tech}</code></div></li>'
        for i, (t, p, tech) in enumerate(steps))
    out_rows = "".join(
        f'<tr><td><code>{a}</code></td><td>{b}</td><td>{d}</td></tr>' for a, b, d in OUTCOMES)
    return f'''
<section class="sec first">
  <h2>How the pieces fit</h2>
  {pair("A schedule starts the run. A browser opens each site as a consistent visitor. A platform-specific adapter does the clicking. Results go to a database and problems go to your phone.",
        "Seven stages, numbered below in run order. Everything site-specific sits in config and in the adapter layer, so the first four stages are written once and reused by all " + str(r["summary"]["active_sites"]) + " sites.")}
  <div class="diagram">{architecture_svg(r)}</div>
</section>

<section class="sec">
  <h2>One claim, step by step</h2>
  <ol class="steps7">{steps_html}</ol>
</section>

<section class="sec">
  <h2>When something goes wrong</h2>
  <p class="lede">Every claim ends in exactly one of these outcomes. Each has a fixed response, so a failure is never silent.</p>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Outcome</th><th>What it means</th><th>What the bot does</th></tr></thead>
    <tbody>{out_rows}</tbody>
  </table></div>
</section>
'''


def panel_sites(r, c):
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    ordered = sorted(c["active"], key=lambda s: (tier_rank[s["tier"]], s["name"].lower()))
    rows = ""
    for site in ordered:
        d = c["diffs"].get(site["name"], 0)
        exp = expected_daily(site)
        days = site["min_redeem"] / exp if exp > 0 else None
        mk = MECH[site["mechanism"]]["key"] if site["mechanism"] in MECH else "click"
        ml = MECH[site["mechanism"]]["label"] if site["mechanism"] in MECH else site["mechanism"]
        parent = site["parent"] if site["parent"] not in ("", "Unknown") else "Not listed"
        capped = site["daily_max"] > DAILY_CAP
        rng = f'{money(site["daily_min"])} – {money(eff_max(site))}{"+" if capped else ""}'
        days_txt = "no daily" if days is None else (">365 d" if days > 365 else f"{days:.0f} d")
        n_res = len(site["restricted"])
        res_title = ", ".join(site["restricted"]) if n_res else "none listed"
        rows += (
            f'<tr data-tier="{site["tier"]}" data-q="{e((site["name"] + " " + parent + " " + ml).lower())}">'
            f'<td data-v="{e(site["name"].lower())}"><b>{e(site["name"])}</b></td>'
            f'<td data-v="{tier_rank[site["tier"]]}">{tier_badge(site["tier"])}</td>'
            f'<td data-v="{e(parent.lower())}" class="muted">{e(parent)}</td>'
            f'<td data-v="{e(ml)}"><span class="mtag m-{mk}">{e(ml)}</span></td>'
            f'<td data-v="{exp:.3f}" class="num" title="Expected {money(exp)} per day">{rng}</td>'
            f'<td data-v="{site["min_redeem"]}" class="num">{site["min_redeem"]}</td>'
            f'<td data-v="{days if days is not None else 99999:.1f}" class="num">{days_txt}</td>'
            f'<td data-v="{d}">{diff_cell(d)}</td>'
            f'<td data-v="{n_res}" class="num" title="{e(res_title)}">{n_res}</td></tr>')
    counts = {t: sum(1 for s in c["active"] if s["tier"] == t) for t in TIER_ORDER}
    chips = f'<button class="chip" type="button" data-tier="all" aria-pressed="true">All <b>{len(c["active"])}</b></button>' + "".join(
        f'<button class="chip" type="button" data-tier="{t}" aria-pressed="false">{TIER_LABEL[t]} <b>{counts[t]}</b></button>' for t in TIER_ORDER)
    return f'''
<section class="sec first">
  <h2>All {len(c["active"])} active sites</h2>
  <p class="lede">Search, filter by tier, or click a column heading to sort. Hover the daily yield for the expected figure and the blocked-states count for the state list.</p>
  <div class="toolbar">
    <label class="search"><span class="sr">Search sites</span><input id="q" type="search" placeholder="Search by site, parent company or claim type" autocomplete="off"></label>
    <div class="chips" role="group" aria-label="Filter by tier">{chips}</div>
    <span class="count" id="count" aria-live="polite">{len(c["active"])} of {len(c["active"])}</span>
  </div>
  <div class="tbl-wrap tall"><table class="sortable" id="sites">
    <thead><tr><th>Site</th><th>Tier</th><th>Platform family</th><th>Claim type</th><th class="num">Daily yield</th><th class="num">Redeems at</th><th class="num">~Days to payout</th><th>Est. difficulty</th><th class="num">Blocked states</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
  <p class="note">Difficulty is a 1–5 estimate from the claim type, the number of blocked states (more states, more proxy work) and the parent company’s known anti-bot posture. It is replaced by measured values once live probing starts.</p>
</section>
'''


def histogram(buckets, color):
    peak = max(v for _, v in buckets) or 1
    return '<div class="bars">' + "".join(
        bar_row(lbl, f"{v} sites", v / peak, color) for lbl, v in buckets) + "</div>"


def panel_risk(r, c):
    h = r["health"]
    flagged = "".join(f'<tr><td><b>{e(x["name"])}</b></td><td>{e(x["reason"])}</td></tr>' for x in h["risky"])
    dead = " · ".join(h["dead"])

    dist = {}
    for d in c["diffs"].values():
        dist[d] = dist.get(d, 0) + 1
    diff_buckets = [(f"{k:.1f}", dist[k]) for k in sorted(dist)]

    edges = [("under 60 days", 0, 60), ("60 to 120", 60, 120), ("120 to 240", 120, 240),
             ("240 to 365", 240, 365), ("over a year", 365, 10 ** 9)]
    run_buckets = [(lbl, sum(1 for d in c["days"] if lo <= d < hi)) for lbl, lo, hi in edges]

    return f'''
<section class="sec first">
  <h2>Site health</h2>
  <div class="health">
    <div class="h good"><b>{len(h["healthy"])}</b><span>no flags in the notes</span></div>
    <div class="h warn"><b>{len(h["risky"])}</b><span>flagged for a risk</span></div>
    <div class="h bad"><b>{len(h["dead"])}</b><span>closed or no daily bonus</span></div>
  </div>
  <p class="note">Closed or removed from scope: {e(dead)}.</p>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Flagged site</th><th>Reason from the masterlist</th></tr></thead>
    <tbody>{flagged}</tbody>
  </table></div>
</section>

<section class="sec">
  <div class="two">
    <div>
      <h2>Automation difficulty</h2>
      <p class="lede">Number of sites at each estimated difficulty score (1 easy, 5 hard).</p>
      {histogram(diff_buckets, "--accent")}
    </div>
    <div>
      <h2>Time to first payout</h2>
      <p class="lede">Days for one site to reach its minimum redemption at the expected daily rate. Median {c["median_days"]} days.</p>
      {histogram(run_buckets, "--accent")}
    </div>
  </div>
  {pair("Most sites take months to reach a payout, and a few take over a year. The bot’s job is to keep every account active and claiming every day until it gets there.",
        "Days = minimum redemption ÷ expected daily yield, for the " + str(len(c["days"])) + " sites with a daily bonus. Two sites (Cluck, Lucky Slots .us) list no free daily amount and are left out.")}
</section>

<section class="sec">
  <h2>What this analysis cannot see</h2>
  <ul class="limits">
    <li><b>Platform grouping comes from the masterlist, not from the live sites.</b> Some independent-looking sites may share a white-label platform, which would lower the adapter count further.</li>
    <li><b>Difficulty is estimated.</b> The real anti-bot setup of each site (Cloudflare Turnstile, DataDome, PerimeterX or none) needs live probing.</li>
    <li><b>Yield assumes every bonus can be claimed.</b> Purchase-locked and VIP-locked sites will return nothing until the owner unlocks them.</li>
    <li><b>Site terms.</b> Most sweepstakes sites restrict automated access in their terms of use. The bot reduces the chance of being flagged but cannot remove it, and an account that is closed may lose its balance. Redeeming balances regularly limits that exposure.</li>
  </ul>
</section>
'''


def panel_build(r, c, adapter_code, config_code):
    timed = r["mechanisms"].get(TIMED, {}).get("sites", [])
    n_god = sum(1 for s in c["active"] if s["tier"] == GOD)
    n_rest = len(c["active"]) - n_god
    checks = [
        "Compare page structure inside each family to confirm one adapter really covers all its sites.",
        "Identify the anti-bot vendor on each platform and measure which sites show CAPTCHAs.",
        "List sites that need a phone code at login (Fliff does) and decide how those are handled.",
        "Confirm each site’s redemption rules against the masterlist before balances are tracked.",
    ]
    checks_html = "".join(f"<li>{x}</li>" for x in checks)
    return f'''
<section class="sec first">
  <h2>Build plan</h2>
  <div class="phases">
    <article class="phase">
      <span class="tag">Phase 1 · weeks 1 to 2</span>
      <h3>Core engine and the {n_god} God-tier sites</h3>
      <ul>
        <li>Orchestrator, scheduler, session factory and browser pool</li>
        <li>Fingerprint profiles, residential proxies and the encrypted credential vault</li>
        <li>Adapters for the {n_god} God-tier sites, built family by family</li>
        <li>Results database, Telegram alerts and the monitoring dashboard</li>
      </ul>
      <p class="milestone">Working demo on real accounts by day 5.</p>
    </article>
    <article class="phase">
      <span class="tag">Phase 2 · weeks 3 to 5</span>
      <h3>Remaining {n_rest} sites and multi-user groundwork</h3>
      <ul>
        <li>Adapters for the High, Medium and Trash tiers</li>
        <li>Interval engine for the {len(timed)} timed sites ({e(", ".join(timed))})</li>
        <li>UI-change detection with screenshots and automatic platform pause</li>
        <li>Per-user accounts and separated credentials, so the bot can become a service</li>
      </ul>
      <p class="milestone">All active sites covered, handover notes written.</p>
    </article>
  </div>
  <h3 class="sub">Checks in week 1</h3>
  <ul class="limits">{checks_html}</ul>
</section>

<section class="sec">
  <h2>Code from this analysis</h2>
  <p class="lede">The adapter contract and the config format the build starts from. The adapter is a working pattern with placeholder selectors, which are replaced with real ones when each live site is inspected.</p>
  <details class="code" open>
    <summary><span>adapter_interface.py</span><em>Base class and a full B2 example</em></summary>
    <div class="code-bar"><button type="button" class="btn" data-copy="code-adapter">Copy</button><button type="button" class="btn" data-download="code-adapter" data-name="adapter_interface.py">Download</button></div>
    <pre id="code-adapter"><code>{e(adapter_code)}</code></pre>
  </details>
  <details class="code">
    <summary><span>config.example.json</span><em>Scheduler, anti-detection, vault, alerts, sample sites</em></summary>
    <div class="code-bar"><button type="button" class="btn" data-copy="code-config">Copy</button><button type="button" class="btn" data-download="code-config" data-name="config.example.json">Download</button></div>
    <pre id="code-config"><code>{e(config_code)}</code></pre>
  </details>
</section>
'''


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
CSS = r"""
/* Layout: masthead, sticky tab bar, one panel at a time. White ground, cobalt for action,
   semantic colours only for state. Hairlines do the structure; cards only for real objects. */
:root{
  color-scheme: light;
  --bg:#ffffff; --panel:#f6f8fb; --panel-2:#eaeff6; --line:#e1e6ee; --line-2:#cdd5e1;
  --ink:#0e1726; --ink-2:#44526a; --ink-3:#76839a;
  --accent:#1b44e6; --accent-ink:#1736b8; --accent-bg:#edf1ff;
  --good:#0b7f57; --good-bg:#e6f5ee; --warn:#9a5d06; --warn-bg:#fcf1dc; --bad:#b93131; --bad-bg:#fbeaea;
  --tf-god:#e0a526; --tf-high:#1b44e6; --tf-medium:#97a4b9; --tf-trash:#d86a6a;
  --m-click:#1b44e6; --m-wheel:#0b8a8a; --m-streak:#d98a1f; --m-multi:#5a6a85; --m-timed:#7b57e0; --m-locked:#c23a3a; --m-vip:#b4538f;
  --f-display:"Bricolage Grotesque","Avenir Next","Segoe UI",system-ui,sans-serif;
  --f-body:"IBM Plex Sans","Segoe UI",system-ui,-apple-system,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font:400 15px/1.6 var(--f-body);-webkit-font-smoothing:antialiased}
.wrap{max-width:1160px;margin-inline:auto;padding-inline:clamp(16px,4vw,32px)}
code{font:500 .86em var(--f-mono);background:var(--panel-2);padding:1px 5px;border-radius:4px;color:var(--ink)}
h1,h2,h3,h4{font-family:var(--f-display);color:var(--ink);text-wrap:balance}
a{color:var(--accent)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.muted{color:var(--ink-2)}
.good{color:var(--good);font-weight:600}

/* Masthead */
.mast{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-block:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font:600 17px var(--f-display);letter-spacing:-.01em}
.by{font:500 12px var(--f-mono);color:var(--ink-3);letter-spacing:.02em}
.by b{color:var(--ink);font-weight:600}

/* Hero */
.hero{padding-block:34px 30px;display:grid;gap:26px}
.eyebrow{font:500 12px var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.hero h1{font-size:clamp(34px,6vw,60px);line-height:1.02;letter-spacing:-.03em;font-weight:700;max-width:20ch;margin-top:10px}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero .lede{max-width:64ch;color:var(--ink-2);font-size:16.5px;margin-top:16px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-block:1px solid var(--line)}
.stat{padding:16px 18px 16px 0;display:grid;gap:2px}
.stat + .stat{padding-left:18px;border-left:1px solid var(--line)}
.stat b{font:600 28px/1.1 var(--f-mono);letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat span{font-size:13px;color:var(--ink-2)}
@media (max-width:640px){
  .stats{grid-template-columns:1fr 1fr}
  .stat{border-left:0!important;padding:14px 12px 14px 0!important;border-top:1px solid var(--line)}
  .stat:nth-child(-n+2){border-top:0}
  .stat:nth-child(even){padding-left:16px!important;border-left:1px solid var(--line)!important}
  .stat:last-child{grid-column:1/-1}
}

/* Tabs */
.tabs{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}
.tabs-in{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.tabs-in::-webkit-scrollbar{display:none}
.tab{appearance:none;background:none;border:0;border-bottom:2px solid transparent;padding:15px 14px 13px;font:500 14px var(--f-body);color:var(--ink-2);cursor:pointer;white-space:nowrap;transition:color .15s,border-color .15s}
.tab:hover{color:var(--ink)}
.tab[aria-selected="true"]{color:var(--accent-ink);border-bottom-color:var(--accent);font-weight:600}
.tab small{font:500 11px var(--f-mono);color:var(--ink-3);margin-left:6px}
.panel{padding-block:8px 72px}
.panel[hidden]{display:none}

/* Sections */
.sec{margin-top:44px}
.sec.first{margin-top:34px}
.sec h2{font-size:clamp(22px,3vw,28px);letter-spacing:-.02em;line-height:1.15;margin-bottom:14px}
.sec h3.sub{font-size:18px;margin:28px 0 10px}
.lede{color:var(--ink-2);max-width:70ch;margin-bottom:16px}
.note{color:var(--ink-2);font-size:13.5px;max-width:78ch;margin-top:14px}
.tag{display:block;font:500 11px var(--f-mono);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-bottom:6px}

/* Plain / technical pair */
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:6px}
.pair > div{padding:16px 18px;border-radius:10px;min-width:0}
.pair p{font-size:14.5px}
.plain{background:var(--accent-bg)}
.plain .tag{color:var(--accent-ink)}
.tech{background:var(--panel);border:1px solid var(--line)}
.tech p{color:var(--ink-2);font-size:14px}
@media (max-width:760px){.pair{grid-template-columns:1fr}}

/* Daily flow */
.steps4{list-style:none;display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.steps4 li{padding:18px;display:grid;gap:8px;align-content:start;min-width:0}
.steps4 li + li{border-left:1px solid var(--line)}
.steps4 h4{font-size:18px;letter-spacing:-.01em}
.steps4 p{font-size:14px;color:var(--ink-2)}
.step-n{font:600 12px var(--f-mono);color:var(--accent-ink);background:var(--accent-bg);width:26px;height:26px;border-radius:50%;display:grid;place-items:center;flex:none}
.line{font:400 12px/1.5 var(--f-mono);color:var(--ink-3);background:none;padding:0;display:block}
@media (max-width:900px){.steps4{grid-template-columns:1fr 1fr}.steps4 li:nth-child(3){border-left:0}.steps4 li:nth-child(n+3){border-top:1px solid var(--line)}}
@media (max-width:520px){.steps4{grid-template-columns:1fr}.steps4 li{border-left:0!important}.steps4 li + li{border-top:1px solid var(--line)}}

/* Findings */
.finds{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--line)}
.finds > div{padding:18px 22px 6px 0;min-width:0}
.finds > div + div{padding-left:22px;border-left:1px solid var(--line)}
.finds b{font:600 clamp(34px,5vw,52px)/1 var(--f-display);letter-spacing:-.03em;color:var(--ink)}
.finds b small{font:500 14px var(--f-body);letter-spacing:0;color:var(--ink-3);margin-left:6px}
.finds p{margin-top:10px;font-size:14.5px;color:var(--ink-2);max-width:34ch}
@media (max-width:760px){.finds{grid-template-columns:1fr}.finds > div + div{padding-left:0;border-left:0;border-top:1px solid var(--line);margin-top:14px;padding-top:18px}}

/* Bars */
.bars{display:grid;gap:12px;margin-top:6px}
.bar-row{display:grid;grid-template-columns:170px 1fr 112px;gap:14px;align-items:center}
.bar-label{font-size:14px;display:grid;gap:2px;min-width:0}
.bar-label small{font-size:12px;color:var(--ink-3)}
.bar-track{height:12px;background:var(--panel-2);border-radius:3px;overflow:hidden}
.bar-track i{display:block;height:100%;border-radius:3px}
.bar-val{font:500 13px var(--f-mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
@media (max-width:560px){.bar-row{grid-template-columns:1fr auto}.bar-track{grid-column:1/-1;order:3}}
.range{display:grid;grid-template-columns:repeat(3,1fr);margin-top:26px;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.range > div{padding:16px 18px;display:grid;gap:2px;min-width:0}
.range > div + div{border-left:1px solid var(--line)}
.range span{font:500 11px var(--f-mono);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)}
.range b{font:600 26px var(--f-mono);letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.range small{font-size:12.5px;color:var(--ink-2)}
.range .mid{background:var(--accent-bg)}
.range .mid b{color:var(--accent-ink)}
@media (max-width:560px){.range{grid-template-columns:1fr}.range > div + div{border-left:0;border-top:1px solid var(--line)}}

/* Badges, squares, tags */
.badge{display:inline-block;font:600 11px var(--f-mono);letter-spacing:.05em;text-transform:uppercase;padding:2px 8px;border-radius:4px;white-space:nowrap}
.badge.t-god{background:#fbf0d4;color:#85530a}
.badge.t-high{background:var(--accent-bg);color:var(--accent-ink)}
.badge.t-medium{background:var(--panel-2);color:var(--ink-2)}
.badge.t-trash{background:var(--bad-bg);color:var(--bad)}
.sq{display:block;width:15px;height:15px;border-radius:3px;flex:none}
.sq.t-god{background:var(--tf-god)}.sq.t-high{background:var(--tf-high)}.sq.t-medium{background:var(--tf-medium)}.sq.t-trash{background:var(--tf-trash)}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:13px;color:var(--ink-2);align-items:center;margin-bottom:16px}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend.spread{margin-top:12px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;flex:none}
.mtag{display:inline-block;font:500 12px var(--f-body);padding:2px 8px;border-radius:4px;background:var(--panel-2);color:var(--ink);margin:1px 3px 1px 0;white-space:nowrap}
.m-click.dot,.stack .m-click{background:var(--m-click)}.m-wheel.dot,.stack .m-wheel{background:var(--m-wheel)}.m-streak.dot,.stack .m-streak{background:var(--m-streak)}
.m-multi.dot,.stack .m-multi{background:var(--m-multi)}.m-timed.dot,.stack .m-timed{background:var(--m-timed)}.m-locked.dot,.stack .m-locked{background:var(--m-locked)}.m-vip.dot,.stack .m-vip{background:var(--m-vip)}

/* Families */
.fams{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.fam{border:1px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:12px;align-content:start;min-width:0}
.fam.wide{grid-column:1/-1}
.fam-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
.fam-head b{font:600 17px var(--f-display);letter-spacing:-.01em}
.fam-head span{font:500 12px var(--f-mono);color:var(--accent-ink)}
.sqs{display:flex;flex-wrap:wrap;gap:4px}
.fam-sites{font-size:13px;color:var(--ink-2)}

/* Claim types */
.stack{display:flex;height:16px;border-radius:4px;overflow:hidden;gap:2px}
.stack i{display:block;height:100%;min-width:3px}
.legend b{font:600 12px var(--f-mono);color:var(--ink);margin-left:2px}
.mgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;margin-top:22px}
.mcard{border:1px solid var(--line);border-radius:12px;padding:18px;display:grid;gap:10px;align-content:start;min-width:0}
.mhead{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.mhead h3{font-size:18px;letter-spacing:-.01em}
.mcount{margin-left:auto;font:500 12px var(--f-mono);color:var(--ink-3)}
.mcard p{font-size:14.5px;color:var(--ink-2)}
.mcard .mtech{background:var(--panel);border-radius:8px;padding:10px 12px;font-size:13.5px}
.msites{font-size:12.5px!important;color:var(--ink-3)!important}

/* Architecture */
.diagram{margin-top:16px;border:1px solid var(--line);border-radius:12px;padding:12px;overflow-x:auto}
.arch{display:block;width:100%;min-width:760px;height:auto}
.arch .node{fill:#fff;stroke:var(--line-2);stroke-width:1.2}
.arch .node.soft{fill:var(--panel);stroke-dasharray:4 4}
.arch .layer{fill:var(--panel);stroke:var(--line-2);stroke-width:1.2;stroke-dasharray:5 5}
.arch .card{fill:#fff;stroke:var(--line-2)}
.arch .card.more{fill:var(--accent-bg);stroke:#b9c7fb}
.arch .strip{fill:#fff;stroke:var(--line-2);stroke-dasharray:3 4}
.arch .s-title{font:600 14px var(--f-body);fill:var(--ink)}
.arch .s-sub{font:400 12px var(--f-body);fill:var(--ink-2)}
.arch .s-tiny{font:400 11px var(--f-body);fill:var(--ink-3)}
.arch .s-count{font:500 12px var(--f-mono);fill:var(--accent-ink)}
.arch .s-layer{font:500 11px var(--f-mono);letter-spacing:.09em;fill:var(--ink-3)}
.arch .s-badge{fill:var(--accent-bg);stroke:#b9c7fb}
.arch .s-step{font:600 11px var(--f-mono);fill:var(--accent-ink)}
.arch .s-arrow{stroke:var(--accent);stroke-width:1.6;fill:none}
.arch .s-head{fill:var(--accent)}
.steps7{list-style:none;display:grid;border-top:1px solid var(--line)}
.steps7 li{display:grid;grid-template-columns:34px 1fr;gap:14px;padding:16px 0;border-bottom:1px solid var(--line)}
.steps7 h4{font-size:17px;letter-spacing:-.01em;margin-bottom:2px}
.steps7 p{font-size:14.5px;color:var(--ink-2);max-width:80ch}
.steps7 .line{margin-top:6px;max-width:100ch}

/* Tables */
.tbl-wrap{border:1px solid var(--line);border-radius:12px;overflow:auto}
.tbl-wrap.tall{max-height:640px}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:640px}
#sites{min-width:980px}
th{position:sticky;top:0;background:var(--panel);text-align:left;font:500 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);padding:11px 14px;border-bottom:1px solid var(--line);white-space:nowrap;z-index:1}
th.num{text-align:right}
td{padding:11px 14px;border-top:1px solid var(--line);vertical-align:top}
tbody tr:first-child td{border-top:0}
tbody tr:hover td{background:#fbfcfe}
.sortable th{cursor:pointer;user-select:none}
.sortable th:hover{color:var(--ink)}
.sortable th[aria-sort="ascending"]::after{content:" ▲";color:var(--accent)}
.sortable th[aria-sort="descending"]::after{content:" ▼";color:var(--accent)}
td code{white-space:nowrap}
.diff{display:inline-flex;align-items:center;gap:8px}
.diff-track{width:54px;height:6px;background:var(--panel-2);border-radius:3px;overflow:hidden}
.diff-track i{display:block;height:100%}
.diff b{font:600 12px var(--f-mono)}
.d-easy i{background:var(--good)}.d-mid i{background:#d98a1f}.d-hard i{background:var(--bad)}

/* Directory toolbar */
.toolbar{display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center;margin-bottom:14px}
.search{flex:1 1 280px;min-width:0}
.search input{width:100%;font:400 14px var(--f-body);padding:10px 14px;border:1px solid var(--line-2);border-radius:8px;background:#fff;color:var(--ink)}
.search input:focus{border-color:var(--accent);outline:2px solid var(--accent-bg)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{appearance:none;font:500 13px var(--f-body);padding:7px 12px;border:1px solid var(--line-2);border-radius:8px;background:#fff;color:var(--ink-2);cursor:pointer}
.chip b{font:600 11px var(--f-mono);margin-left:4px;color:var(--ink-3)}
.chip:hover{border-color:var(--ink-3);color:var(--ink)}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.chip[aria-pressed="true"] b{color:#d6defc}
.count{font:500 12px var(--f-mono);color:var(--ink-3);margin-left:auto}

/* Risk */
.health{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.h{border-radius:12px;padding:16px 18px;display:grid;gap:2px}
.h b{font:600 38px/1 var(--f-display);letter-spacing:-.03em}
.h span{font-size:13.5px}
.h.good{background:var(--good-bg);color:var(--good);font-weight:400}.h.warn{background:var(--warn-bg);color:var(--warn)}.h.bad{background:var(--bad-bg);color:var(--bad)}
.h span{color:var(--ink-2)}
.health + .note{margin-bottom:18px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:36px;margin-bottom:22px}
.two > div{min-width:0}
@media (max-width:820px){.two{grid-template-columns:1fr}.health{grid-template-columns:1fr}}
.limits{display:grid;gap:12px;list-style:none;max-width:80ch}
.limits li{font-size:14.5px;color:var(--ink-2);padding-left:18px;position:relative}
.limits li::before{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;border-radius:2px;background:var(--accent)}
.limits b{color:var(--ink)}

/* Build plan */
.phases{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:820px){.phases{grid-template-columns:1fr}}
.phase{border:1px solid var(--line);border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:10px;min-width:0}
.phase .milestone{margin-top:auto}
.phase h3{font-size:20px;letter-spacing:-.015em}
.phase ul{list-style:none;display:grid;gap:8px}
.phase li{font-size:14.5px;color:var(--ink-2);padding-left:18px;position:relative}
.phase li::before{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;border-radius:2px;background:var(--line-2)}
.milestone{font:500 13px var(--f-mono);color:var(--accent-ink);background:var(--accent-bg);padding:8px 12px;border-radius:8px}
details.code{border:1px solid var(--line);border-radius:12px;margin-top:14px;overflow:hidden}
details.code summary{cursor:pointer;padding:14px 18px;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap;list-style:none;background:var(--panel)}
details.code summary::-webkit-details-marker{display:none}
details.code summary::before{content:"▸";color:var(--ink-3);transition:transform .15s}
details.code[open] summary::before{transform:rotate(90deg)}
details.code summary span{font:600 14px var(--f-mono)}
details.code summary em{font-style:normal;font-size:13px;color:var(--ink-3)}
.code-bar{display:flex;gap:8px;padding:10px 18px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.btn{appearance:none;font:500 12.5px var(--f-body);padding:6px 12px;border:1px solid var(--line-2);border-radius:6px;background:#fff;color:var(--ink);cursor:pointer}
.btn:hover{border-color:var(--accent);color:var(--accent-ink)}
pre{font:400 12.5px/1.6 var(--f-mono);padding:16px 18px;overflow:auto;max-height:520px;background:#fff;color:var(--ink)}
pre code{background:none;padding:0;font:inherit;color:inherit}

/* Footer */
.foot{border-top:1px solid var(--line);padding-block:26px 40px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--ink-3)}
.foot b{color:var(--ink)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

JS = r"""
(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));
  var panels = {};
  tabs.forEach(function (t) { panels[t.dataset.tab] = document.getElementById('panel-' + t.dataset.tab); });
  var bar = document.querySelector('.tabs');

  function show(id, fromUser) {
    if (!panels[id]) id = tabs[0].dataset.tab;
    tabs.forEach(function (t) {
      var on = t.dataset.tab === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      panels[t.dataset.tab].hidden = !on;
    });
    var active = document.getElementById('tab-' + id);
    if (active && active.scrollIntoView) active.scrollIntoView({ block: 'nearest', inline: 'center' });
    if (fromUser) {
      try { history.replaceState(null, '', '#' + id); } catch (e) { /* ignore */ }
      if (bar.getBoundingClientRect().top <= 0) {
        window.scrollTo({ top: bar.offsetTop - 1, behavior: 'auto' });
      }
    }
  }

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(t.dataset.tab, true); });
    t.addEventListener('keydown', function (ev) {
      var n = null;
      if (ev.key === 'ArrowRight') n = (i + 1) % tabs.length;
      else if (ev.key === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
      else if (ev.key === 'Home') n = 0;
      else if (ev.key === 'End') n = tabs.length - 1;
      if (n !== null) { ev.preventDefault(); tabs[n].focus(); show(tabs[n].dataset.tab, true); }
    });
  });
  window.addEventListener('hashchange', function () { show(location.hash.slice(1), false); });
  show(location.hash.slice(1), false);

  /* Sortable tables: cells carry a data-v sort key */
  document.querySelectorAll('table.sortable').forEach(function (table) {
    var heads = table.querySelectorAll('th');
    heads.forEach(function (th, col) {
      th.addEventListener('click', function () {
        var dir = th.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
        heads.forEach(function (h) { h.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', dir);
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function (a, b) {
          var va = a.cells[col].dataset.v !== undefined ? a.cells[col].dataset.v : a.cells[col].textContent.trim();
          var vb = b.cells[col].dataset.v !== undefined ? b.cells[col].dataset.v : b.cells[col].textContent.trim();
          var na = Number(va), nb = Number(vb);
          var numeric = va !== '' && vb !== '' && isFinite(na) && isFinite(nb);
          var r = numeric ? na - nb : String(va).localeCompare(String(vb));
          return dir === 'ascending' ? r : -r;
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  });

  /* Directory: search + tier filter */
  var input = document.getElementById('q');
  var chips = document.querySelectorAll('.chip');
  var rows = document.querySelectorAll('#sites tbody tr');
  var count = document.getElementById('count');
  var tier = 'all';
  function apply() {
    var q = (input.value || '').toLowerCase().trim();
    var shown = 0;
    rows.forEach(function (r) {
      var ok = (tier === 'all' || r.dataset.tier === tier) && (!q || r.dataset.q.indexOf(q) !== -1);
      r.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown + ' of ' + rows.length;
  }
  if (input) input.addEventListener('input', apply);
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      tier = c.dataset.tier;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      apply();
    });
  });

  /* Code: copy + download */
  function flash(btn, text) {
    var old = btn.textContent; btn.textContent = text;
    setTimeout(function () { btn.textContent = old; }, 1400);
  }
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var txt = document.getElementById(b.dataset.copy).textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(function () { flash(b, 'Copied'); }, function () { fallback(txt, b); });
      } else { fallback(txt, b); }
    });
  });
  function fallback(txt, b) {
    var ta = document.createElement('textarea'); ta.value = txt; document.body.appendChild(ta);
    ta.select(); try { document.execCommand('copy'); flash(b, 'Copied'); } catch (e) { flash(b, 'Select and copy'); }
    document.body.removeChild(ta);
  }
  document.querySelectorAll('[data-download]').forEach(function (b) {
    b.addEventListener('click', function () {
      var txt = document.getElementById(b.dataset.download).textContent;
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([txt], { type: 'text/plain' }));
      a.download = b.dataset.name; document.body.appendChild(a); a.click(); document.body.removeChild(a);
    });
  });
})();
"""


def render(results):
    c = build_context(results)
    s, rev = results["summary"], results["revenue"]
    adapter_code = open(os.path.join(ROOT, "site", "files", "adapter_interface.py")).read()
    config_code = open(os.path.join(ROOT, "site", "files", "config.example.json")).read()

    tabs = [
        ("overview", "Overview", panel_overview(results, c), None),
        ("families", "Platform map", panel_families(results, c), None),
        ("claims", "Claim types", panel_claims(results, c), None),
        ("architecture", "Architecture", panel_architecture(results, c), None),
        ("sites", "Site directory", panel_sites(results, c), str(len(c["active"]))),
        ("risk", "Risk and payout", panel_risk(results, c), None),
        ("build", "Build plan", panel_build(results, c, adapter_code, config_code), None),
    ]
    tab_btns = "".join(
        f'<button class="tab" role="tab" id="tab-{i}" data-tab="{i}" aria-controls="panel-{i}" '
        f'aria-selected="{"true" if k == 0 else "false"}" tabindex="{0 if k == 0 else -1}">{label}'
        f'{f"<small>{n}</small>" if n else ""}</button>'
        for k, (i, label, _, n) in enumerate(tabs))
    panel_html = "".join(
        f'<div class="panel" role="tabpanel" id="panel-{i}" aria-labelledby="tab-{i}"{"" if k == 0 else " hidden"}>'
        f'<div class="wrap">{body}</div></div>'
        for k, (i, _, body, _) in enumerate(tabs))

    logo = ('<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true">'
            + "".join(
                f'<rect x="{x}" y="{y}" width="6" height="6" rx="1.5" fill="{"#1b44e6" if (x, y) == (8, 8) else "#cdd5e1"}"/>'
                for x in (1, 8, 15) for y in (1, 8, 15))
            + "</svg>")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sweeps Intelligence</title>
<meta name="description" content="Technical map of {s["total_sites"]} sweepstakes sites: platform families, claim types, architecture, risk and build plan.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="wrap mast">
  <div class="brand">{logo}Sweeps Intelligence</div>
  <div class="by">Prepared by <b>{AUTHOR}</b> · Casino Masterlist, updated 2026-09-21</div>
</header>

<section class="wrap hero">
  <div>
    <div class="eyebrow">Site recon · {s["total_sites"]} sites surveyed</div>
    <h1>Build <em>{s["unique_adapters"]}</em> adapters, not {s["active_sites"]}.</h1>
    <p class="lede">The masterlist has {s["total_sites"]} sites and {s["dead_sites"]} are closed. The other {s["active_sites"]} run on {s["unique_adapters"]} distinct platforms, because {s["multi_site_families"]} parent companies operate {s["sites_in_families"]} of them. This report maps every site, claim type, risk and cost so the build can be planned before any bot code is written.</p>
  </div>
  <div class="stats">
    <div class="stat"><b>{s["active_sites"]}</b><span>active sites</span></div>
    <div class="stat"><b>{s["unique_adapters"]}</b><span>adapters to build</span></div>
    <div class="stat"><b>{s["multi_site_families"]}</b><span>shared platform families</span></div>
    <div class="stat"><b>{money(rev["daily_expected"])}</b><span>expected per day</span></div>
    <div class="stat"><b>{c["median_days"]} d</b><span>median time to first payout</span></div>
  </div>
</section>

<nav class="tabs" aria-label="Report sections"><div class="wrap"><div class="tabs-in" role="tablist">{tab_btns}</div></div></nav>

<main>{panel_html}</main>

<footer class="wrap foot">
  <span>Prepared by <b>{AUTHOR}</b>. Built from the masterlist spreadsheet. No live site was scraped.</span>
  <span>Parent companies, blocked states and bonus amounts are as reported in the source.</span>
</footer>
<script>{JS}</script>
</body>
</html>'''


if __name__ == "__main__":
    results = run_analysis()
    page = render(results)
    out_dir = os.path.join(ROOT, "site")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(page)
    print(f"Generated {os.path.normpath(out_path)} ({len(page):,} bytes)")

    data_dir = os.path.join(ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "analysis.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("Saved data/analysis.json")
