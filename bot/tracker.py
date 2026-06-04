# bot/tracker.py
from datetime import datetime

class TradeTracker:
    def __init__(self, max_trades_per_day=5):
        self.max_trades = max_trades_per_day
        self.user_trades = {}  # chat_id: {date: count}

    def can_trade(self, chat_id):
        today = datetime.utcnow().date()
        if chat_id not in self.user_trades:
            self.user_trades[chat_id] = {}
        if today not in self.user_trades[chat_id]:
            self.user_trades[chat_id][today] = 0
        return self.user_trades[chat_id][today] < self.max_trades

    def record_trade(self, chat_id):
        today = datetime.utcnow().date()
        if chat_id not in self.user_trades:
            self.user_trades[chat_id] = {}
        if today not in self.user_trades[chat_id]:
            self.user_trades[chat_id][today] = 0
        self.user_trades[chat_id][today] += 1

    def trades_left(self, chat_id):
        today = datetime.utcnow().date()
        if chat_id not in self.user_trades or today not in self.user_trades[chat_id]:
            return self.max_trades
        return self.max_trades - self.user_trades[chat_id][today]