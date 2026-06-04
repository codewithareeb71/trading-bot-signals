from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .market_data import last_close_price, get_trend
from .logger import logger


# =========================
# FINAL SIGNAL MODEL (MATCH BOT)
# =========================
@dataclass
class TradeSignal:
    symbol: str
    direction: str        # BUY / SELL / NEUTRAL
    entry_time: str
    expiry_time: str
    confidence: float
    price: float
    trend: str


# =========================
# ENGINE
# =========================
def generate_signal(symbol: str) -> Optional[TradeSignal]:

    try:
        price = last_close_price(symbol)
        trend_data = get_trend(symbol)

        # DEBUG (important)
        print("PRICE:", price)
        print("TREND:", trend_data)

        if price is None or price <= 0:
            logger.warning("No market data for %s", symbol)
            return None

        direction_raw = "UNKNOWN"

        if isinstance(trend_data, dict):
            direction_raw = trend_data.get("direction", "UNKNOWN")

        # DEFAULT
        direction = "NEUTRAL"
        confidence = 0.45

        # BUY
        if direction_raw == "bullish":
            direction = "BUY"
            confidence = 0.75 + min(price * 0.01, 0.05)

        # SELL
        elif direction_raw == "bearish":
            direction = "SELL"
            confidence = 0.75 + min(price * 0.01, 0.05)

        else:
            direction = "NEUTRAL"
            confidence = 0.40

        # clamp confidence
        confidence = max(0.30, min(confidence, 0.90))

        now = datetime.utcnow()

        return TradeSignal(
            symbol=symbol,
            direction=direction,
            entry_time=now.strftime("%H:%M UTC"),
            expiry_time=(now + timedelta(minutes=1)).strftime("%H:%M UTC"),
            confidence=round(confidence, 2),
            price=float(price),
            trend=direction_raw
        )

    except Exception as e:
        print("ENGINE ERROR:", e)
        return None