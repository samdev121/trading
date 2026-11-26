from __future__ import annotations

from datetime import date, timedelta


# NSE/CMTR/71775, dated 12-Dec-2025. These are regular full-day trading
# holidays. Weekend holidays and the special Muhurat session are excluded.
NSE_2026_TRADING_HOLIDAYS = frozenset({
    date(2026, 1, 26),
    date(2026, 3, 3),
    date(2026, 3, 26),
    date(2026, 3, 31),
    date(2026, 4, 3),
    date(2026, 4, 14),
    date(2026, 5, 1),
    date(2026, 5, 28),
    date(2026, 6, 26),
    date(2026, 9, 14),
    date(2026, 10, 2),
    date(2026, 10, 20),
    date(2026, 11, 10),
    date(2026, 11, 24),
    date(2026, 12, 25),
})


def is_trading_day(day: date, holidays: frozenset[date] = NSE_2026_TRADING_HOLIDAYS) -> bool:
    return day.weekday() < 5 and day not in holidays


def previous_trading_day(day: date, holidays: frozenset[date] = NSE_2026_TRADING_HOLIDAYS) -> date:
    candidate = day
    while not is_trading_day(candidate, holidays):
        candidate -= timedelta(days=1)
    return candidate


def nifty_weekly_expiries(start: date, end: date) -> list[date]:
    """Return Tuesday expiries adjusted to the previous NSE trading day."""
    cursor = start - timedelta(days=start.weekday())
    expiries: list[date] = []
    while cursor <= end + timedelta(days=7):
        tuesday = cursor + timedelta(days=1)
        expiry = previous_trading_day(tuesday)
        if start <= expiry <= end:
            expiries.append(expiry)
        cursor += timedelta(days=7)
    return sorted(set(expiries))


def expiry_for_code(session: date, expiry_code: int, calendar_end: date) -> date | None:
    """Map observed Dhan code 1=current, 2=next, 3=far to an expiry."""
    expiries = [expiry for expiry in nifty_weekly_expiries(session, calendar_end) if expiry >= session]
    position = expiry_code - 1
    return expiries[position] if 0 <= position < len(expiries) else None
