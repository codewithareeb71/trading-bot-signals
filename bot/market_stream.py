import yfinance as yf
import time
import threading

LIVE_CACHE = {}

SYMBOLS = ["EURUSD=X", "GBPUSD=X", "BTC-USD", "GC=F"]


def fetch_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if data.empty:
            return None
        return float(data["Close"].iloc[-1])
    except:
        return None


def update_market_data():
    while True:
        for symbol in SYMBOLS:
            LIVE_CACHE[symbol] = fetch_price(symbol)
        time.sleep(5)


def start_market_stream():
    thread = threading.Thread(target=update_market_data, daemon=True)
    thread.start()