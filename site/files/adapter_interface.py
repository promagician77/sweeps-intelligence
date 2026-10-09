"""
Base adapter interface for sweepstakes site automation.
Each platform family implements one adapter; sites sharing a parent company
inherit the same adapter with only config differences (URL, branding CSS selectors).

This is the contract every adapter fulfills. The orchestrator calls these
methods and doesn't know which site it's talking to.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import datetime


class ClaimResult(Enum):
    SUCCESS       = "success"        # bonus claimed
    ALREADY_CLAIMED = "already_claimed"  # already collected today
    WHEEL_SPUN    = "wheel_spun"     # wheel spin completed (amount in .value_sc)
    STREAK_DAY    = "streak_day"     # streak day recorded (amount in .value_sc)
    PURCHASE_REQUIRED = "purchase_req"  # daily locked behind a package
    VIP_REQUIRED  = "vip_required"   # daily locked behind VIP level
    SITE_DOWN     = "site_down"      # site unreachable or in maintenance
    LOGIN_FAILED  = "login_failed"   # credentials rejected or 2FA required
    CAPTCHA       = "captcha"        # CAPTCHA not solved
    UI_CHANGED    = "ui_changed"     # expected element not found (adapter broken)
    ERROR         = "error"          # unexpected error


@dataclass
class ClaimOutcome:
    result:    ClaimResult
    value_sc:  float = 0.0           # SC earned this claim
    balance:   Optional[float] = None  # current SC balance if readable
    message:   str = ""              # human-readable detail
    screenshot: Optional[bytes] = None  # PNG for debugging / proof
    timestamp: datetime.datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow()


class SiteAdapter(ABC):
    """
    One adapter per platform family.
    Sites on the same platform (e.g., all B2 sites) share this class;
    each site passes its own config (URL, selectors, credentials).
    """

    def __init__(self, site_config: dict, browser_context):
        """
        site_config: from config.json — has url, credentials ref, selectors
        browser_context: Playwright BrowserContext with its own fingerprint
        """
        self.config = site_config
        self.ctx = browser_context
        self.page = None

    @abstractmethod
    async def login(self) -> bool:
        """
        Log into the site. Returns True on success.
        Should handle: cookie-based session restore, fresh login,
        and detecting 2FA or CAPTCHA prompts.
        """
        ...

    @abstractmethod
    async def claim_daily(self) -> ClaimOutcome:
        """
        Navigate to the daily bonus and claim it.
        This is the core method. It should:
        1. Navigate to the bonus page (URL or in-app navigation)
        2. Detect if already claimed today
        3. Click the claim button / spin the wheel / etc.
        4. Read the result (SC earned)
        5. Return a ClaimOutcome

        The orchestrator calls this once per day per site (or per interval
        for timed sites like Fliff/Jefebet).
        """
        ...

    @abstractmethod
    async def check_balance(self) -> Optional[float]:
        """Read current SC balance. Returns None if not readable."""
        ...

    async def is_healthy(self) -> bool:
        """
        Quick health check: can we reach the site and see the expected page?
        Used by the orchestrator to detect site outages or UI changes
        without doing a full claim cycle.
        """
        try:
            page = await self.ctx.new_page()
            resp = await page.goto(self.config["url"], timeout=15000)
            ok = resp and resp.status == 200
            await page.close()
            return ok
        except Exception:
            return False

    async def cleanup(self):
        """Close pages and release resources."""
        if self.page:
            await self.page.close()


# ---------------------------------------------------------------------------
# Example: B2 family adapter (McLuck, Playfame, Hello Millions, Jackpota,
#          SpinBlitz, MegaBonanza — 6 sites, 1 adapter)
# ---------------------------------------------------------------------------

class B2Adapter(SiteAdapter):
    """
    B2 Entertainment platform. All 6 B2 sites share the same SPA shell,
    the same bonus modal, and the same API endpoints. The only differences
    are the domain and the CSS theme.
    """

    async def login(self) -> bool:
        self.page = await self.ctx.new_page()
        # Try session restore first (cookies from previous run)
        await self.page.goto(self.config["url"])
        if await self._is_logged_in():
            return True
        # Fresh login
        await self.page.goto(f'{self.config["url"]}/login')
        await self.page.fill(self.config["selectors"]["email_input"],
                             self.config["credentials"]["email"])
        await self.page.fill(self.config["selectors"]["password_input"],
                             self.config["credentials"]["password"])
        await self.page.click(self.config["selectors"]["login_button"])
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        return await self._is_logged_in()

    async def claim_daily(self) -> ClaimOutcome:
        if not self.page:
            if not await self.login():
                return ClaimOutcome(ClaimResult.LOGIN_FAILED)
        try:
            # B2 sites expose daily bonus via a modal triggered by a nav icon
            daily_btn = self.config["selectors"].get("daily_button",
                            '[data-testid="daily-bonus"], .daily-reward-btn')
            await self.page.click(daily_btn, timeout=5000)
            await self.page.wait_for_timeout(1500)  # animation

            # Check if already claimed
            claimed_el = await self.page.query_selector(
                self.config["selectors"].get("already_claimed",
                    '.already-claimed, .bonus-collected'))
            if claimed_el:
                return ClaimOutcome(ClaimResult.ALREADY_CLAIMED,
                                   message="Daily already collected")

            # Click claim
            claim_btn = self.config["selectors"].get("claim_button",
                            '.claim-btn, [data-action="claim"]')
            await self.page.click(claim_btn, timeout=5000)
            await self.page.wait_for_timeout(2000)

            # Read amount
            amount_el = await self.page.query_selector(
                self.config["selectors"].get("amount_display",
                    '.reward-amount, .sc-earned'))
            amount_text = await amount_el.inner_text() if amount_el else "0"
            value = self._parse_sc(amount_text)

            balance = await self.check_balance()
            return ClaimOutcome(ClaimResult.SUCCESS, value_sc=value,
                                balance=balance,
                                message=f"Claimed {value} SC")
        except Exception as e:
            return ClaimOutcome(ClaimResult.UI_CHANGED,
                                message=f"Selector miss: {e}")

    async def check_balance(self) -> Optional[float]:
        try:
            bal_el = await self.page.query_selector(
                self.config["selectors"].get("balance",
                    '.sc-balance, [data-testid="balance"]'))
            if bal_el:
                text = await bal_el.inner_text()
                return self._parse_sc(text)
        except Exception:
            pass
        return None

    async def _is_logged_in(self) -> bool:
        return bool(await self.page.query_selector(
            self.config["selectors"].get("logged_in_indicator",
                '.user-avatar, [data-testid="profile"]')))

    @staticmethod
    def _parse_sc(text: str) -> float:
        import re
        m = re.search(r'[\d.]+', text.replace(',', ''))
        return float(m.group()) if m else 0.0
