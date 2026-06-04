from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .market_data import last_close_price, get_trend
from .logger import logger


# ALL PAIRS SUPPORT
SYMBOLS = [
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "USD_CHF",
    "AUD_USD",
    "USD_CAD",
    "NZD_USD",
    "EUR_GBP",
    "GBP_JPY",
    "USD_TRY"
]


@dataclass
class TradeSignal:
    symbol: str
    direction: str
    entry_time: str
    expiry_time: str
    confidence: float
    price: float
    trend: str
    message: str


def generate_signal(symbol: str = None) -> Optional[TradeSignal]:

    try:
        # if no symbol → auto scan best pair
        pairs = [symbol] if symbol else SYMBOLS

        best_signal = None
        best_conf = 0

        for sym in pairs:

            price = last_close_price(sym)
            trend_data = get_trend(sym)

            if price is None:
                continue

            direction_raw = trend_data.get("direction", "UNKNOWN") if isinstance(trend_data, dict) else "UNKNOWN"

            if direction_raw not in ["bullish", "bearish"]:
                continue

            direction = "BUY" if direction_raw == "bullish" else "SELL"

            # confidence logic (strong filter)
            confidence = 0.60

            if direction_raw == "bullish":
                confidence += 0.15
            if direction_raw == "bearish":
                confidence += 0.15

            confidence = round(min(confidence, 0.90), 2)

            # skip weak trades
            if confidence < 0.70:
                continue

            if confidence > best_conf:
                best_conf = confidence
                now = datetime.utcnow()

                best_signal = TradeSignal(
                    symbol=sym,
                    direction=direction,
                    entry_time=now.strftime("%H:%M UTC"),
                    expiry_time=(now + timedelta(minutes=2)).strftime("%H:%M UTC"),
                    confidence=confidence,
                    price=float(price),
                    trend=direction_raw,
                    message="Strong market confirmation"
                )

        return best_signal

    except Exception as e:
        logger.error("ENGINE ERROR: %s", e)
        return None