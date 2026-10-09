"""
All 87 sites from the Casino Masterlist spreadsheet (updated 2026-09-21).
Each site carries the fields the adapter system needs: parent company,
bonus mechanism, daily yield range, minimum redemption, and restricted states.

Source: https://docs.google.com/spreadsheets/d/1F4k-OlRZGxzQ094cxEAQIXP0Qmg3tTJWW3SsPZCAfjo
"""

# Mechanism constants
CLICK    = "click"       # simple claim button
WHEEL    = "wheel"       # spin wheel with variable outcome
STREAK   = "streak"      # consecutive-day calendar
TIMED    = "timed"       # multiple claims per day (every N hours)
MULTI    = "multi_step"  # multi-step navigation (Get Coins -> Daily Bonus)
LOCKED   = "purchase_locked"  # requires a purchase to unlock daily
VIP      = "vip_locked"  # requires VIP level
MOBILE   = "mobile_only" # phone login required
NONE     = "none"        # no daily bonus / closed

# Tier constants
GOD   = "god"
HIGH  = "high"
MED   = "medium"
TRASH = "trash"
DEAD  = "dead"

SITES = [
    # ================================================================= GOD TIER
    {"name": "Crown Coins",        "tier": GOD,   "parent": "Sunflower Limited",
     "mechanism": STREAK, "daily_min": 0.05, "daily_max": 1.50, "min_redeem": 50,
     "notes": "VIP increases daily rewards",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","LA","MI","MT","NV","WA"]},

    {"name": "McLuck",             "tier": GOD,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 2.00, "min_redeem": 75,
     "notes": "Three tiered purchase offers",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","OH","WA","WV"]},

    {"name": "WOW Vegas",          "tier": GOD,   "parent": "MW Services",
     "mechanism": LOCKED, "daily_min": 0.10, "daily_max": 0.10, "min_redeem": 100,
     "notes": "Daily locked without a package purchase",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","ID","MI","MT","NV","WA"]},

    {"name": "Legendz",            "tier": GOD,   "parent": "Platinum Panther LTD",
     "mechanism": CLICK, "daily_min": 1.50, "daily_max": 1.50, "min_redeem": 100,
     "notes": "Daily expires after 10 days; resets after package purchase",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","KY","ID","MI","MT","NE","ND","OH","WA","NY","WV","TN","NV"]},

    {"name": "Real Prize",         "tier": GOD,   "parent": "RealPlay Tech Inc",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Giveaways; restricted by VIP level for some games",
     "daily_hint": "Daily Rewards",
     "restricted": ["AR","GA","HI","ID","KY","MI","MS","NE","NV","NY","ND","TN","VT","WA"]},

    {"name": "Lonestar",           "tier": GOD,   "parent": "RealPlay Tech Inc",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 1.30, "min_redeem": 100,
     "notes": "Free $1 links available",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","MT","NV","WA"]},

    {"name": "LuckyLandSlots",     "tier": GOD,   "parent": "VGW",
     "mechanism": STREAK, "daily_min": 0.30, "daily_max": 1.00, "min_redeem": 50,
     "notes": "$1/day after 7-day streak",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","ID","WA","NV","MI","DE","MT","MS"]},

    {"name": "LuckyLandCasino",    "tier": GOD,   "parent": "VGW",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 50,
     "notes": "2 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","LA","MI","MS","MT","NV","NJ","NY","WA","WV"]},

    {"name": "GoldTreasureCasino", "tier": GOD,   "parent": "Miracle Studio Inc",
     "mechanism": STREAK, "daily_min": 0.50, "daily_max": 1.50, "min_redeem": 100,
     "notes": "~1 SC average + day 7 wheel",
     "daily_hint": "Daily Rewards",
     "restricted": ["GA","HI","ID","MI","MS","NE","NV","NY","ND","OH","TN","VT","WA","WY"]},

    {"name": "Playfame",           "tier": GOD,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 75,
     "notes": "$10/30SC (300%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","OH","WA","WV"]},

    {"name": "Luckparty",          "tier": GOD,   "parent": "Unknown",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 50,
     "notes": "",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","WA","NY"]},

    {"name": "Hello Millions",     "tier": GOD,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.40, "min_redeem": 75,
     "notes": "$24.99/60SC (240%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","OH","WA","WV"]},

    {"name": "MyPrize",            "tier": GOD,   "parent": "My Technology Inc",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 2.00, "min_redeem": 100,
     "notes": "Streak calendar",
     "daily_hint": "Daily Rewards",
     "restricted": ["HI","ID","LA","MI","MT","NV","NY","WA"]},

    {"name": "Chumba Casino",      "tier": GOD,   "parent": "VGW",
     "mechanism": STREAK, "daily_min": 0.25, "daily_max": 5.00, "min_redeem": 100,
     "notes": "Daily scales from $0.25 to $5 over a week",
     "daily_hint": "Daily Rewards (Get Coins -> Daily Bonus)",
     "restricted": ["CT","ID","MI","MT","DE","NV","WA","MS"]},

    {"name": "Moozi",              "tier": GOD,   "parent": "Moshy Gaming",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Holiday logins",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","NV","ID","MI"]},

    {"name": "LuckyBitsVegas",     "tier": GOD,   "parent": "LBV Social LLC",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 95,
     "notes": "First 30 days $1.00; 3x playthrough",
     "daily_hint": "Daily Rewards",
     "restricted": ["AZ","CT","DE","ID","KY","LA","MD","MI","MT","NV","NJ","NY","PA","RI","WA","WV"]},

    {"name": "Pulsz",              "tier": GOD,   "parent": "Yellow Social",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Some packages can be bought repeatedly",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","MT","NV","WA","AZ","MS"]},

    {"name": "PulszBingo",         "tier": GOD,   "parent": "Yellow Social",
     "mechanism": WHEEL, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$40/80SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","ID","LA","MI","MS","MT","NV","NY","TN","WA","AZ","WV"]},

    {"name": "Sportzino",          "tier": GOD,   "parent": "Blazesoft",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 2.00, "min_redeem": 50,
     "notes": "$5/15SC (300%)",
     "daily_hint": "Daily Rewards (Coin Store)",
     "restricted": ["GA","ID","MI","NV","NY","WA"]},

    {"name": "Zula",               "tier": GOD,   "parent": "Blazesoft",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 50,
     "notes": "$300/600SC or $150/300SC",
     "daily_hint": "Daily Rewards (Coin Store)",
     "restricted": ["ID","MI","NV","WA","NY"]},

    {"name": "YayCasino",          "tier": GOD,   "parent": "Blazesoft",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 50,
     "notes": "$10/20SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NY","NV","KY","VT","WA"]},

    {"name": "SpinSaga",           "tier": GOD,   "parent": "SpinSaga Inc",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$26/50SC (192%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","MT","NE","NV","ND","WA"]},

    {"name": "Rolla",              "tier": GOD,   "parent": "MW Services",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "First 30 days $1.00; $9.99/29.99SC (167%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","ID","MI","MT","NV","NY","WA"]},

    {"name": "Stake",              "tier": GOD,   "parent": "Sweepsteaks Limited",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 50,
     "notes": "Crypto-focused; 25 SC signup via referral",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","KY","MI","NV","NJ","NY","PA","RI","VT","WA","WV","MD"]},

    {"name": "Casino.Click",       "tier": GOD,   "parent": "Casino Click",
     "mechanism": WHEEL, "daily_min": 0.00, "daily_max": 5.00, "min_redeem": 100,
     "notes": "$10/25SC (250%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","KY","WA"]},

    {"name": "Global Poker",       "tier": GOD,   "parent": "VGW",
     "mechanism": MULTI, "daily_min": 0.25, "daily_max": 1.00, "min_redeem": 50,
     "notes": "",
     "daily_hint": "Daily Rewards (Get Coins)",
     "restricted": ["CT","ID","MI","MT","NV","DE","WA","MS"]},

    {"name": "Stackr",             "tier": GOD,   "parent": "Stackr Social LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 2.20, "min_redeem": 100,
     "notes": "$0.20 + wheel $0.10-$2.00; four packs at 150%",
     "daily_hint": "Daily Rewards",
     "restricted": ["AZ","CA","CO","CT","DE","FL","HI","IL","IN","KS","ME","MD","MN","MT","NJ","NC","OR","RI","SD","VA","WI","WY"]},

    {"name": "SpinPals",           "tier": GOD,   "parent": "SpinPals LLC",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$10/25SC (250%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","ID","LA","MI","MT","NV","WA"]},

    # ================================================================= HIGH TIER
    {"name": "Sixty6",             "tier": HIGH,  "parent": "Kinetix Ventures LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 5.00, "min_redeem": 100,
     "notes": "Redemption cancellation problems reported",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","KY","MD","MI","MT","NV","NY","WA","WV","MS","AZ"]},

    {"name": "Card Crush",         "tier": HIGH,  "parent": "Vision NL Limited",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.50, "min_redeem": 75,
     "notes": "Random free drops; 5 cards + 25 coins for $9.99; only CA and NY",
     "daily_hint": "Daily Rewards",
     "restricted": []},  # available only in CA and NY — inverse restriction

    {"name": "Sidepot",            "tier": HIGH,  "parent": "Fliff",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 6.00, "min_redeem": 100,
     "notes": "Capped at $6; $19.99/40SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","ID","KY","LA","MI","MT","NV","TN","WA"]},

    {"name": "RubySweeps",         "tier": HIGH,  "parent": "Rubystone Ventures LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 1.00, "min_redeem": 50,
     "notes": "100% match with code",
     "daily_hint": "Daily Rewards (Daily Spin)",
     "restricted": ["CT","DE","ID","MI","NE","KY","OH","RI","UT","WA"]},

    {"name": "RichSweeps",         "tier": HIGH,  "parent": "WW Funcrafters JWA LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 20.00, "min_redeem": 100,
     "notes": "$9.99/30SC, $24.99/50SC, $49.99/65SC",
     "daily_hint": "Daily Rewards (Daily Spin Wheel on Top)",
     "restricted": ["CT","DE","HI","ID","LA","MI","MT","NV","NY","WA"]},

    {"name": "SweepsRoyal",        "tier": HIGH,  "parent": "WW Funcrafters JWA LLC",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "Up to 200% on first purchase",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","HI","ID","LA","MI","MT","NV","NJ","NY","WA"]},

    {"name": "Shuffle.us",         "tier": HIGH,  "parent": "Munyon Canyon",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.40, "min_redeem": 100,
     "notes": "Starts at $0.10",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","FL","GA","HI","ID","KY","LA","MD","MI","MT","NV","NJ","NY","PA","RI","VT","WA","WV"]},

    {"name": "American Luck",      "tier": HIGH,  "parent": "Munyon Canyon",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 1.50, "min_redeem": 100,
     "notes": "$4.99/15SC (300%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","LA","MI","MT","NV","NJ","NY","WA"]},

    {"name": "ScarletSands",       "tier": HIGH,  "parent": "UTech Solutions",
     "mechanism": STREAK, "daily_min": 0.25, "daily_max": 10.00, "min_redeem": 100,
     "notes": "$0.25-$0.50 + day 7 spins + wheel $1-$10",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","LA","MI","MT","NV","NJ","NY","RI","WA","WV","WY"]},

    {"name": "Golden Hearts Games","tier": HIGH,  "parent": "Golden Hearts",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","ID","NV","MI"]},

    {"name": "SweepNext",          "tier": HIGH,  "parent": "Boostora LTD",
     "mechanism": MULTI, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$9.99/25SC (150%); Mega Spin under Top Left Sidebar",
     "daily_hint": "Daily Rewards (Mega Spin under Top Left Sidebar)",
     "restricted": ["CT","ID","LA","MD","MI","MT","NV","NY"]},

    {"name": "ReBet",              "tier": HIGH,  "parent": "Rebet Inc",
     "mechanism": MULTI, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 20,
     "notes": "Capped at 1SC; $200/300SC (200%)",
     "daily_hint": "Daily Rewards (Profile -> ReBet Cash)",
     "restricted": []},

    {"name": "Fliff",              "tier": HIGH,  "parent": "Fliff",
     "mechanism": TIMED, "daily_min": 1.00, "daily_max": 2.20, "min_redeem": 50,
     "notes": "$1 + $0.10 every 2 hours",
     "daily_hint": "Login on Phone",
     "restricted": ["HI","ID","NV","TN","WA"]},

    {"name": "MoonSpin",           "tier": HIGH,  "parent": "Star Pulse Limited",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 6.00, "min_redeem": 100,
     "notes": "Capped at $6; $19.99/40SC (200%); redemption problems",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","MT","MI","NV","LA","ID","NE","ND","GA"]},

    {"name": "ToraTora",           "tier": HIGH,  "parent": "ToraTora Entertainment Inc",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 5.00, "min_redeem": 50,
     "notes": "Spin: 1SC, 5SC, or coins",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","KY","LA","MD","MI","MS","MT","NE","NV","NY","WA","WV"]},

    {"name": "SpinDoo",            "tier": HIGH,  "parent": "PMSG Media Limited",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 2.00, "min_redeem": 75,
     "notes": "B2 site; launched Oct 2025",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","WA","WV"]},

    {"name": "SpeedSweeps",        "tier": HIGH,  "parent": "WW Funcrafters JWA LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 20.00, "min_redeem": 100,
     "notes": "$9.99/30SC, $24.99/50SC, $49.99/65SC",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","HI","ID","LA","MD","MI","MT","NV","WA"]},

    # ================================================================= MEDIUM TIER
    {"name": "Sweepshark",         "tier": MED,   "parent": "UTech Solutions",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "Day 7 spins; $49.99 for $100 (100%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","LA","MI","MT","NV","NJ","NY","RI","WA","WV","WY"]},

    {"name": "DimeSweeps",         "tier": MED,   "parent": "WW Funcrafters JWA LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 20.00, "min_redeem": 100,
     "notes": "$9.99/30SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","HI","ID","LA","MI","MT","NV","NJ","NY","WA"]},

    {"name": "PeakPlay",           "tier": MED,   "parent": "Rubystone Play LLC",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.50, "min_redeem": 100,
     "notes": "Daily contests; $20/40SC (100%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","ID","GA","LA","MD","MI","MT","NV","PA","RI","TN","WA","WV"]},

    {"name": "Jefebet",            "tier": MED,   "parent": "FSG Digital",
     "mechanism": TIMED, "daily_min": 0.80, "daily_max": 1.40, "min_redeem": 100,
     "notes": "$0.80 start, then $0.20 every 6 hours",
     "daily_hint": "Daily Rewards (Get Coins)",
     "restricted": ["CT","DE","HI","ID","KY","LA","MD","MI","MT","NV","NJ","WA"]},

    {"name": "Rolling Riches",     "tier": MED,   "parent": "Rolling Riches",
     "mechanism": TIMED, "daily_min": 0.80, "daily_max": 1.40, "min_redeem": 100,
     "notes": "$0.80 start, then $0.20 every 6 hours",
     "daily_hint": "Daily Rewards",
     "restricted": ["CA","CT","DE","HI","ID","IL","KY","LA","MD","MI","MT","NV","NJ","NY","TN","WA","WV"]},

    {"name": "Fortune Coins",      "tier": MED,   "parent": "Blazesoft",
     "mechanism": MULTI, "daily_min": 0.75, "daily_max": 0.75, "min_redeem": 50,
     "notes": "",
     "daily_hint": "Daily Rewards (Get Coins)",
     "restricted": ["ID","MI","NV","NY","WA"]},

    {"name": "Clubs Poker",        "tier": MED,   "parent": "KHK Games Inc",
     "mechanism": MULTI, "daily_min": 0.50, "daily_max": 0.50, "min_redeem": 100,
     "notes": "$20/40SC (200%)",
     "daily_hint": "Daily Rewards (Get Coins)",
     "restricted": ["ID","NV","MI","MT","LA","MS","WV","WA"]},

    {"name": "High5Casino",        "tier": MED,   "parent": "High 5",
     "mechanism": CLICK, "daily_min": 0.50, "daily_max": 0.50, "min_redeem": 100,
     "notes": "$100 for $110SC (110%); diamonds bonus",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","ID","KY","LA","MD","MI","MS","MT","NV","NJ","NY","PA","RI","WA","WV","AZ"]},

    {"name": "Modo",               "tier": MED,   "parent": "ARB Gaming",
     "mechanism": STREAK, "daily_min": 0.40, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$1 after 4-day streak; $210/300SC (143%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","MT","MD","PA","NJ","CT","WV","LA","RI","DE","NV","MI","ID","NY","AZ"]},

    {"name": "Spree",              "tier": MED,   "parent": "Play Spree",
     "mechanism": CLICK, "daily_min": 0.40, "daily_max": 0.40, "min_redeem": 75,
     "notes": "$10/30SC (300%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","WA","WV","NY","CT"]},

    {"name": "LunaLandCasino",     "tier": MED,   "parent": "Parana Plays LLC",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$0.20 periodic + $1 at 7 days",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","WA"]},

    {"name": "GetZoot",            "tier": MED,   "parent": "Enigma Lake Inc",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.50, "min_redeem": 40,
     "notes": "3 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","LA","MI","NE","NV","ND","WA"]},

    {"name": "LuckyStake",         "tier": MED,   "parent": "ElevateTech Solutions Inc",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 2.00, "min_redeem": 100,
     "notes": "$9.99/25SC (150%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","HI","ID","LA","MD","MI","MT","NV","NY","UT","WA"]},

    {"name": "Ace.com",            "tier": MED,   "parent": "Full Stop Limited Inc",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.40, "min_redeem": 75,
     "notes": "2.5 SC on signup; $9.99/25SC (150%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","PA","RI","TN","WA","WV"]},

    {"name": "NoLimitCoins",       "tier": MED,   "parent": "A1",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Day 7 spins; $11.99/24SC (200%), $40/80SC",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","MI","MT","NV","NY","WA","WV","WY"]},

    {"name": "ChipNWin",           "tier": MED,   "parent": "Chipnwin LLC",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.50, "min_redeem": 100,
     "notes": "$199/266SC (133%), $300/400SC",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","WA"]},

    {"name": "FortuneWheelz",      "tier": MED,   "parent": "A1",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.50, "min_redeem": 100,
     "notes": "$30/70SC (233%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","MI","MT","NV","NY","WA","WV","WY"]},

    {"name": "FunzCity",           "tier": MED,   "parent": "A1",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.50, "min_redeem": 100,
     "notes": "$30/60SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","ID","WY","MI","NV","CT","DE","MT","WV","NY"]},

    {"name": "MegaFrenzy",         "tier": MED,   "parent": "Heuston Gaming Inc",
     "mechanism": MULTI, "daily_min": 0.10, "daily_max": 0.40, "min_redeem": 100,
     "notes": "Daily Bonus under Top Right Star",
     "daily_hint": "Daily Rewards (Daily Bonus under Top Right Star)",
     "restricted": ["CT","ID","LA","MD","MI","MT","NV","NY","WA"]},

    {"name": "TaoFortune",         "tier": MED,   "parent": "A1",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Spins; $80/110SC (137.5%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","MI","MT","NV","NY","WA","WV","WY"]},

    {"name": "FunRize",            "tier": MED,   "parent": "A1",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Spins; $24.99/60SC (240%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","MI","MT","NV","NY","WA","WV","WY"]},

    {"name": "Chanced.com",        "tier": MED,   "parent": "Gold Coin Group",
     "mechanism": STREAK, "daily_min": 0.00, "daily_max": 1.00, "min_redeem": 100,
     "notes": "$1 after 5-day streak; 20 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","KY","WA","MT","WV","DE","CT"]},

    {"name": "SpinQuest",          "tier": MED,   "parent": "Social Gaming Room LLC",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 1.00, "min_redeem": 50,
     "notes": "$10/30SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","ID","MI","MT","NV","NY","WA"]},

    {"name": "Jackpota",           "tier": MED,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 75,
     "notes": "$10/25SC (250%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","PA","WA","WV"]},

    {"name": "SpinBlitz",          "tier": MED,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 50,
     "notes": "$10/10SC + spins, incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","OH","WA","WV"]},

    {"name": "MegaBonanza",        "tier": MED,   "parent": "B2",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 75,
     "notes": "$10/25SC (250%), incremental",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","ID","KY","LA","MD","MI","MT","NV","NJ","NY","OH","PA","WA","WV"]},

    {"name": "AcornFun",           "tier": MED,   "parent": "Jupiter Studio Limited",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 0.30, "min_redeem": 100,
     "notes": "Streak calendar ($0.30 / $0.20 / 10 spins)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","FL","GA","ID","KY","MI","MN","NV","SC","WA"]},

    {"name": "Baba Casino",        "tier": MED,   "parent": "Baba Entertainment LTD",
     "mechanism": CLICK, "daily_min": 0.25, "daily_max": 0.25, "min_redeem": 100,
     "notes": "$9.99/25SC (250%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AR","CT","DE","GA","HI","ID","IA","KY","MI","MS","MT","NE","NV","NY","ND","OH","TN","VT","WA"]},

    {"name": "Dara Casino",        "tier": MED,   "parent": "Dara Casino",
     "mechanism": CLICK, "daily_min": 0.25, "daily_max": 0.25, "min_redeem": 100,
     "notes": "",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","HI","ID","KY","MI","MS","MT","NV","NY","ND","OH","TN","VT","WA"]},

    {"name": "JackpotRabbit",      "tier": MED,   "parent": "UTech Solutions",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "$29.99/60SC or $24.99/50SC (200%)",
     "daily_hint": "Daily Rewards (Daily Bonus on right under Menu)",
     "restricted": ["CT","DE","ID","MI","MT","NV","NY","WA","WV","WY"]},

    {"name": "The Money Factory",  "tier": MED,   "parent": "The Money Factory",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "$8/32SC (400%), incremental; 1-2 month redemption delays",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","LA","MI","MT","NV","WA"]},

    {"name": "Sheeshcasino",       "tier": MED,   "parent": "P8D Interactive Inc",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "$99.99/150SC (50%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","LA","MI","MT","NV","NY","WA"]},

    {"name": "GoodVibesCasino",    "tier": MED,   "parent": "SKEEVE Products Limited",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "$9.99/25SC (150%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","GA","HI","ID","KY","MI","MT","NV","SC","UT","WA"]},

    {"name": "Wild World Casino",  "tier": MED,   "parent": "IGW Wild World LLC",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "",
     "daily_hint": "Daily Rewards",
     "restricted": ["WA","NV","CT","HI","LA","ID"]},

    {"name": "Spinfinite",         "tier": MED,   "parent": "Forever Winning LLC",
     "mechanism": WHEEL, "daily_min": 0.10, "daily_max": 5.00, "min_redeem": 100,
     "notes": "Mostly GC; $20/40SC + wheel",
     "daily_hint": "Daily Rewards (Bonuses tab, Bottom Left)",
     "restricted": ["WA","ID","MI","NV","MT","DE","AL","TN"]},

    {"name": "Luckyhands",         "tier": MED,   "parent": "Lucky Hands",
     "mechanism": MULTI, "daily_min": 0.10, "daily_max": 0.10, "min_redeem": 50,
     "notes": "$15/20SC (133%)",
     "daily_hint": "Daily Rewards (Get Coins -> Daily Bonus)",
     "restricted": ["ID","LA","MI","NV","NY","MT"]},

    {"name": "SorceryReels",       "tier": MED,   "parent": "Fish Bear Studio Limited",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.10, "min_redeem": 100,
     "notes": "0.40 SC + 10 spins on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","MI","NV","WA"]},

    {"name": "Smiles Casino",      "tier": MED,   "parent": "10 Ten Gaming LLC",
     "mechanism": CLICK, "daily_min": 0.05, "daily_max": 0.15, "min_redeem": 100,
     "notes": "$200/250SC (125%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["NV","KY","MI","ID","CT","DE","WA","MD"]},

    {"name": "Cazino",             "tier": MED,   "parent": "Heuston Gaming",
     "mechanism": CLICK, "daily_min": 0.10, "daily_max": 0.10, "min_redeem": 100,
     "notes": "Refills at $0; $9.99/20SC (200%)",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","LA","MD","MI","MT","NV","NJ","WA"]},

    {"name": "Cluck",              "tier": MED,   "parent": "The Roost LTD",
     "mechanism": VIP, "daily_min": 0.00, "daily_max": 0.00, "min_redeem": 100,
     "notes": "Unlocked by VIP level; 2 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","ID","MI","NV","NY","WA","CA"]},

    {"name": "Lucky Slots .us",    "tier": MED,   "parent": "Sweet Innovation LLC",
     "mechanism": CLICK, "daily_min": 0.00, "daily_max": 0.00, "min_redeem": 100,
     "notes": "Under review; 5 SC on signup",
     "daily_hint": "Daily Rewards (Daily Bonuses Tab)",
     "restricted": ["CT","ID","MI","LA","MT","NV","WA","NY","WV"]},

    # ================================================================= TRASH TIER
    {"name": "Lucky.me",           "tier": TRASH, "parent": "Lucky Me Ventures LLC",
     "mechanism": STREAK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "Lucky Streak; 2 SC on signup; redemption problems",
     "daily_hint": "Daily Rewards (Daily Bonus on left side)",
     "restricted": ["CT","ID","MI","NV","NY","WA"]},

    {"name": "GoldSlips",          "tier": TRASH, "parent": "Rubystone Ventures LLC",
     "mechanism": WHEEL, "daily_min": 0.00, "daily_max": 15.00, "min_redeem": 50,
     "notes": "100% match on $5, $10, $20",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","FL","GA","ID","KY","LA","MD","MI","NE","NJ","NY","OH","RI","UT","WA"]},

    {"name": "NioPlay",            "tier": TRASH, "parent": "Nio Consolidated LLC",
     "mechanism": TIMED, "daily_min": 0.30, "daily_max": 1.20, "min_redeem": 75,
     "notes": "$0.30 every 6 hours; 50% bonus match",
     "daily_hint": "Daily Rewards",
     "restricted": ["ID","LA","MI","MT","NV","WA","NY","CT","MD"]},

    {"name": "VegasCoins",         "tier": TRASH, "parent": "Vegas Coins Inc",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "1 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","DE","ID","KY","LA","MI","MT","NV","NY","TN","WA"]},

    {"name": "Lavish Luck",        "tier": TRASH, "parent": "Prudent Owl Limited",
     "mechanism": CLICK, "daily_min": 0.30, "daily_max": 0.30, "min_redeem": 100,
     "notes": "4 boosted packages",
     "daily_hint": "Daily Rewards",
     "restricted": ["CA","CT","DE","ID","KY","LA","MI","MT","NV","NJ","NY","WA"]},

    {"name": "JuicyPopSlots",      "tier": TRASH, "parent": "SWPMTECH LTD",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "3 SC on signup",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","HI","ID","LA","MD","MI","MS","MT","NV","NY","WA","WV"]},

    {"name": "LuckyStars",         "tier": TRASH, "parent": "SWPMTECH LTD",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "3 SC on signup; stopped daily rewards",
     "daily_hint": "Daily Rewards",
     "restricted": ["AL","CT","ID","KY","LA","MI","MT","NV","WA"]},

    {"name": "Vivaro.us",          "tier": TRASH, "parent": "SWS Operations Inc",
     "mechanism": CLICK, "daily_min": 1.00, "daily_max": 50.00, "min_redeem": 100,
     "notes": "$50/65SC (130%); unreliable",
     "daily_hint": "Daily Rewards",
     "restricted": ["FL","GA","HI","ID","KY","MI","MS","MT","NV","NY","ND","OH","TN","VT","WA","DE","WV","MD","LA"]},

    {"name": "GummyPlay",          "tier": TRASH, "parent": "SWPMTECH LTD",
     "mechanism": CLICK, "daily_min": 0.20, "daily_max": 0.20, "min_redeem": 100,
     "notes": "3 SC on signup; closed/unavailable",
     "daily_hint": "Daily Rewards",
     "restricted": ["CT","DE","ID","MD","MI","MS","MT","NV","NJ","NY","WA","WV","DC"]},

    # ================================================================= DEAD / SUNSETTED
    {"name": "Sportsmillions",     "tier": DEAD,  "parent": "B2",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 75,
     "notes": "Sunsetted",
     "daily_hint": "",
     "restricted": []},

    {"name": "Sweepslots",         "tier": DEAD,  "parent": "Regal Technologies",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 100,
     "notes": "Site currently down",
     "daily_hint": "",
     "restricted": []},

    {"name": "Vegas Gems",         "tier": DEAD,  "parent": "Unknown",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 0,
     "notes": "Stopped giving gems",
     "daily_hint": "",
     "restricted": []},

    {"name": "Carnival Citi",      "tier": DEAD,  "parent": "Unknown",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 0,
     "notes": "Dead",
     "daily_hint": "",
     "restricted": []},

    {"name": "Jacks Club",         "tier": DEAD,  "parent": "Unknown",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 0,
     "notes": "Dead",
     "daily_hint": "",
     "restricted": []},

    {"name": "Scrooge",            "tier": DEAD,  "parent": "Unknown",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 0,
     "notes": "Free SC expires after 7 days",
     "daily_hint": "",
     "restricted": []},

    {"name": "Punt",               "tier": DEAD,  "parent": "Unknown",
     "mechanism": NONE, "daily_min": 0, "daily_max": 0, "min_redeem": 0,
     "notes": "Dead",
     "daily_hint": "",
     "restricted": []},
]
