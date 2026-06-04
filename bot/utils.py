from datetime import datetime
from typing import Optional

from .database import get_setting


# =========================
# SIGNAL FORMAT (REAL STYLE)
# =========================
def format_signal_message(signal_data: dict) -> str:
    return (
        f"📊 TRADING SIGNAL\n\n"
        f"Asset: {signal_data.get('symbol', 'N/A')}\n"
        f"Signal: {signal_data.get('signal_type', 'N/A')}\n"
        f"Entry Time (UTC): {signal_data.get('entry_time', 'N/A')}\n"
        f"Expiry Time (UTC): {signal_data.get('expiry_time', 'N/A')}\n"
        f"Confidence: {signal_data.get('confidence', 0) * 100:.1f}%\n"
        f"Trend: {signal_data.get('trend', 'N/A')}\n"
        f"Price: {safe_price(signal_data.get('price'))}\n\n"
        f"Reason: {signal_data.get('technical_reasoning', 'Market structure analysis')}\n\n"
        f"Risk Level: {signal_data.get('risk_warning', 'Moderate')}\n"
    )


# =========================
# MARKET SNAPSHOT (REAL CLEAN)
# =========================
def format_market_message(symbol: str, price: Optional[float], trend: str, note: str = "") -> str:
    return (
        f"📈 MARKET SNAPSHOT\n\n"
        f"Asset: {symbol}\n"
        f"Price: {safe_price(price)}\n"
        f"Trend: {trend}\n"
        f"{note}\n"
    )


# =========================
# HISTORY
# =========================
def format_history(signals: list) -> str:
    if not signals:
        return "No trading history yet."

    lines = ["🧾 RECENT SIGNALS\n"]

    for item in signals:
        lines.append(
            f"{item.get('created_at', '')[:19]} | "
            f"{item.get('symbol', '')} | "
            f"{item.get('signal_type', '')} | "
            f"{item.get('confidence', 0)*100:.0f}%"
        )

    return "\n".join(lines)


# =========================
# SETTINGS
# =========================
def is_signals_enabled() -> bool:
    value = get_setting("signals_enabled")
    return value is None or value == "1"


# =========================
# SYMBOL CLEANER
# =========================
def parse_symbol(text: str) -> str:
    candidate = text.strip().upper()
    return candidate if candidate else "EURUSD=X"


# =========================
# SAFE PRICE HANDLER
# =========================
def safe_price(price) -> str:
    if price is None:
        return "N/A"
    try:
        return f"{float(price):.5f}"
    except Exception:
        return "N/A"


# =========================
# DATETIME FORMATTER
# =========================
def format_datetime_iso(timestamp: str) -> str:
    try:
        return datetime.fromisoformat(
            timestamp.replace("Z", "")
        ).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return timestamp