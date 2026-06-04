from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from .market_data import last_close_price, get_trend
from .logger import logger

@dataclass
class TradeSignal:
    symbol: str
    direction: str        # BUY / SELL / NEUTRAL
    status: str           # ACTIVE / WAIT
    entry_time: str
    expiry_time: str
    confidence: float
    price: float
    trend: str
    message: str
    next_signal: str

def generate_signal(symbol: str, trade_window_minutes: int = 2) -> Optional[TradeSignal]:
    try:
        price = last_close_price(symbol)
        trend_data = get_trend(symbol)
        now = datetime.utcnow()
        next_signal_time = (now + timedelta(minutes=5)).strftime("%H:%M UTC")

        if price is None or price <= 0:
            logger.warning("No market data for %s", symbol)
            return TradeSignal(
                symbol=symbol,
                direction="NEUTRAL",
                status="WAIT",
                entry_time="--",
                expiry_time="--",
                confidence=0,
                price=0,
                trend="UNKNOWN",
                message="Unable to fetch live market data.",
                next_signal=next_signal_time
            )

        direction_raw = trend_data.get("direction", "UNKNOWN") if isinstance(trend_data, dict) else "UNKNOWN"
        direction = "NEUTRAL"
        status = "WAIT"
        confidence = 0.0
        message = "Market is not ready for trade."

        if direction_raw in ["bullish", "bearish"]:
            direction = "BUY" if direction_raw == "bullish" else "SELL"
            confidence = 0.70 + min(price * 0.01, 0.05)
            confidence = round(max(0.30, min(confidence, 0.90)), 2)
            status = "ACTIVE"
            message = f"{direction} trade ready. Execute within {trade_window_minutes} min."
            entry_time = now.strftime("%H:%M UTC")
            expiry_time = (now + timedelta(minutes=trade_window_minutes)).strftime("%H:%M UTC")
        else:
            entry_time = "--"
            expiry_time = "--"

        return TradeSignal(
            symbol=symbol,
            direction=direction,
            status=status,
            entry_time=entry_time,
            expiry_time=expiry_time,
            confidence=confidence,
            price=float(price),
            trend=direction_raw,
            message=message,
            next_signal=next_signal_time
        )
    except Exception as e:
        logger.error("ENGINE ERROR: %s", e)
        return None