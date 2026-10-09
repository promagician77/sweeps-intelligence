"""
Analyze the site data: platform families, mechanism taxonomy,
difficulty scoring, and revenue projections.
"""

import json
from collections import defaultdict
from data import SITES, CLICK, WHEEL, STREAK, TIMED, MULTI, LOCKED, VIP, MOBILE, NONE
from data import GOD, HIGH, MED, TRASH, DEAD


# The spreadsheet's "max" column sometimes holds purchase-pack bonuses
# (e.g. "$9.99/30SC, $24.99/50SC") or jackpot-wheel prizes, not the free daily
# claim. Cap each site's max so those outliers cannot inflate the estimate.
DAILY_CAP = 5.0


def eff_max(s):
    return min(s["daily_max"], DAILY_CAP)


def expected_daily(s):
    """Expected SC/day: 70% weight on the low end, 30% on the (capped) high end."""
    return s["daily_min"] * 0.7 + eff_max(s) * 0.3


def capped_sites():
    return [s["name"] for s in SITES if s["tier"] != DEAD and s["daily_max"] > DAILY_CAP]


def platform_families():
    """Group sites by parent company. Sites sharing a parent share an adapter."""
    families = defaultdict(list)
    for s in SITES:
        p = s["parent"]
        if p and p != "Unknown":
            families[p].append(s)
    # Sort by number of sites descending
    return dict(sorted(families.items(), key=lambda x: -len(x[1])))


def family_stats(families):
    """For each family, compute adapter savings and shared characteristics."""
    stats = []
    for parent, sites in families.items():
        active = [s for s in sites if s["tier"] != DEAD]
        if not active:
            continue
        mechanisms = set(s["mechanism"] for s in active)
        tiers = set(s["tier"] for s in active)
        daily_total_min = sum(s["daily_min"] for s in active)
        daily_total_max = sum(eff_max(s) for s in active)
        stats.append({
            "parent": parent,
            "sites": [s["name"] for s in active],
            "count": len(active),
            "mechanisms": sorted(mechanisms),
            "tiers": sorted(tiers),
            "daily_min": round(daily_total_min, 2),
            "daily_max": round(daily_total_max, 2),
            "adapters_saved": max(0, len(active) - 1),
        })
    return sorted(stats, key=lambda x: -x["count"])


def mechanism_taxonomy():
    """Classify all active sites by bonus mechanism type."""
    taxonomy = defaultdict(list)
    for s in SITES:
        if s["tier"] == DEAD:
            continue
        taxonomy[s["mechanism"]].append(s["name"])
    return dict(taxonomy)


MECHANISM_LABELS = {
    CLICK:  ("Button Click",       "Navigate to daily page, click claim button"),
    WHEEL:  ("Spin Wheel",         "Spin a wheel with variable SC outcome"),
    STREAK: ("Streak Calendar",    "Consecutive-day login; bonus grows over 5-7 days"),
    TIMED:  ("Timed Interval",     "Multiple claims per day (every 2-6 hours)"),
    MULTI:  ("Multi-Step Nav",     "Get Coins -> Daily Bonus, or sidebar navigation"),
    LOCKED: ("Purchase-Locked",    "Daily bonus requires an active coin package"),
    VIP:    ("VIP-Locked",         "Daily bonus requires VIP tier"),
    MOBILE: ("Mobile-Only",        "Must log in from phone app"),
    NONE:   ("No Bonus",           "Site is dead or has no daily reward"),
}


def difficulty_score(site):
    """
    Score 1-5 for automation difficulty.
    Factors: mechanism complexity, anti-bot posture (inferred from
    parent company size), restricted-state list length (proxy complexity).
    """
    score = 1.0

    # Mechanism complexity
    mech_scores = {
        CLICK: 1.0, STREAK: 1.5, MULTI: 2.0, WHEEL: 2.5,
        TIMED: 2.5, LOCKED: 3.0, VIP: 3.5, MOBILE: 4.0, NONE: 0.0,
    }
    score += mech_scores.get(site["mechanism"], 2.0)

    # Large restriction list -> more proxy complexity
    n_restricted = len(site["restricted"])
    if n_restricted > 15:
        score += 1.0
    elif n_restricted > 10:
        score += 0.5

    # Known-hard parent companies (VGW has aggressive anti-bot)
    hard_parents = {"VGW", "High 5", "Fliff"}
    if site["parent"] in hard_parents:
        score += 1.0

    return min(5.0, round(score, 1))


def revenue_projection():
    """Compute daily/monthly revenue from all active sites."""
    active = [s for s in SITES if s["tier"] not in (DEAD,)]
    daily_min = sum(s["daily_min"] for s in active)
    daily_max = sum(eff_max(s) for s in active)
    # Realistic estimate: most wheels land near the low end
    daily_expected = sum(expected_daily(s) for s in active)
    return {
        "active_sites": len(active),
        "daily_min": round(daily_min, 2),
        "daily_max": round(daily_max, 2),
        "daily_expected": round(daily_expected, 2),
        "monthly_expected": round(daily_expected * 30, 2),
        "daily_cap": DAILY_CAP,
        "capped_sites": capped_sites(),
        "by_tier": {
            tier: {
                "count": len([s for s in active if s["tier"] == tier]),
                "daily_expected": round(sum(
                    expected_daily(s) for s in active if s["tier"] == tier
                ), 2),
            }
            for tier in (GOD, HIGH, MED, TRASH)
        },
    }


def site_health():
    """Classify sites by operational health based on notes."""
    healthy, risky, dead_list = [], [], []
    risk_keywords = [
        "cancellation", "problems", "locked", "stopped",
        "under review", "unreliable", "delays", "closed",
        "unavailable", "down",
    ]
    for s in SITES:
        if s["tier"] == DEAD:
            dead_list.append(s["name"])
            continue
        notes_lower = s["notes"].lower()
        if any(kw in notes_lower for kw in risk_keywords):
            risky.append({"name": s["name"], "reason": s["notes"]})
        else:
            healthy.append(s["name"])
    return {"healthy": healthy, "risky": risky, "dead": dead_list}


def run_analysis():
    """Run all analyses and return combined results."""
    fams = platform_families()
    fstats = family_stats(fams)

    # Count unique adapters needed
    multi_site_families = [f for f in fstats if f["count"] > 1]
    single_site_count = len([
        s for s in SITES
        if s["tier"] != DEAD
        and (s["parent"] in ("Unknown", "") or
             sum(1 for s2 in SITES if s2["parent"] == s["parent"] and s2["tier"] != DEAD) == 1)
    ])
    adapters_from_families = len(multi_site_families)
    total_adapters = adapters_from_families + single_site_count
    total_active = len([s for s in SITES if s["tier"] != DEAD])
    adapters_saved = total_active - total_adapters

    # Difficulty per site
    difficulties = []
    for s in SITES:
        if s["tier"] == DEAD:
            continue
        difficulties.append({
            "name": s["name"],
            "tier": s["tier"],
            "parent": s["parent"],
            "mechanism": s["mechanism"],
            "difficulty": difficulty_score(s),
            "daily_min": s["daily_min"],
            "daily_max": eff_max(s),
        })
    difficulties.sort(key=lambda x: -x["difficulty"])

    return {
        "summary": {
            "total_sites": len(SITES),
            "active_sites": total_active,
            "dead_sites": len(SITES) - total_active,
            "unique_adapters": total_adapters,
            "adapters_saved": adapters_saved,
            "multi_site_families": len(multi_site_families),
            "sites_in_families": sum(f["count"] for f in multi_site_families),
        },
        "families": fstats,
        "mechanisms": {
            k: {"label": MECHANISM_LABELS[k][0],
                "description": MECHANISM_LABELS[k][1],
                "sites": v}
            for k, v in mechanism_taxonomy().items()
        },
        "revenue": revenue_projection(),
        "health": site_health(),
        "difficulties": difficulties,
    }


if __name__ == "__main__":
    import os
    results = run_analysis()
    os.makedirs("../data", exist_ok=True)
    with open("../data/analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Sites: {results['summary']['total_sites']}")
    print(f"Active: {results['summary']['active_sites']}")
    print(f"Dead: {results['summary']['dead_sites']}")
    print(f"Unique adapters needed: {results['summary']['unique_adapters']}")
    print(f"Adapters saved by family grouping: {results['summary']['adapters_saved']}")
    print(f"Multi-site families: {results['summary']['multi_site_families']}")
    print(f"Daily revenue (expected): ${results['revenue']['daily_expected']}")
    print(f"Monthly revenue (expected): ${results['revenue']['monthly_expected']}")
