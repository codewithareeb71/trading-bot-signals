# bot/telegram_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .signal_engine import generate_signal
from .config import TELEGRAM_BOT_TOKEN
from datetime import datetime

# =========================
# BOT INIT
# =========================
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# =========================
# CURRENCY LIST
# =========================
CURRENCY_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
    "USD/CAD", "NZD/USD", "EUR/GBP", "GBP/JPY", "USD/TRY"
]

# =========================
# DAILY TRADE COUNTER
# =========================
MAX_TRADES_PER_DAY = 5
trade_counter = {"count": 0, "date": datetime.utcnow().date()}

# =========================
# START HANDLER
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])
    await update.message.reply_text(
        f"👋 Welcome to Trading Bot\n\n"
        f"ℹ️ You can take only {MAX_TRADES_PER_DAY} trades/day.\n"
        f"• Each trade has a 2-minute execution window\n\n"
        "Click below to get live signals 👇",
        reply_markup=keyboard
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trade_counter
    query = update.callback_query
    await query.answer()

    # Reset daily counter if date changed
    if trade_counter["date"] != datetime.utcnow().date():
        trade_counter["count"] = 0
        trade_counter["date"] = datetime.utcnow().date()

    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text("⚠️ Daily trade limit reached! Come back tomorrow.")
        return

    data = query.data
    if data == "get_signal":
        # pick best signal from all currencies
        best_signal = None
        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY", "SELL"]:
                if not best_signal or sig.confidence > best_signal.confidence:
                    best_signal = sig
        if not best_signal:
            await query.message.reply_text("❌ No strong signal available now.")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best_signal)

# =========================
# SEND SIGNAL
# =========================
async def send_signal(query, context, sig):
    image_path = "assets/buy.png" if sig.direction == "BUY" else "assets/sell.png"
    caption = (
        f"🟢 <b>{sig.direction} SIGNAL</b>\n\n"
        f"💱 Pair: {sig.symbol}\n"
        f"📊 Direction: {sig.direction}\n"
        f"🔥 Confidence: {sig.confidence}%\n"
        f"💰 Price: {sig.price} USD\n"
        f"⏰ Entry: {sig.entry_time}\n"
        f"⌛ Expiry: {sig.expiry_time}\n"
        f"💬 {sig.message}"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ WIN", callback_data="win"),
            InlineKeyboardButton("❌ LOSS", callback_data="loss")
        ],
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])
    try:
        with open(image_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        await query.message.reply_text(f"⚠️ IMAGE ERROR: {str(e)}")

# =========================
# RUN BOT
# =========================
def run_bot():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 Bot running...")
    app.run_polling()