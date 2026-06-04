from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .signal_engine import generate_signal
from .config import TELEGRAM_BOT_TOKEN
from datetime import datetime

# =========================
# CURRENCY PAIRS
# =========================
CURRENCY_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
    "USD_CAD", "NZD_USD", "EUR_GBP", "GBP_JPY", "USD_TRY"
]

# =========================
# DAILY TRADE LIMIT
# =========================
MAX_TRADES_PER_DAY = 5
trade_counter = {"count": 0, "date": datetime.utcnow().date()}

# =========================
# BOT INIT
# =========================
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trade_counter
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    await update.message.reply_text(
        "👋 Trading Bot Ready\n\n"
        f"📌 Rules:\n• Max Trades/Day: {MAX_TRADES_PER_DAY}\n"
        "• Only high confidence signals\n"
        "• 2 min trade window\n\n"
        "👇 Click button to start",
        reply_markup=keyboard
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trade_counter
    query = update.callback_query
    await query.answer()

    # Reset daily
    if trade_counter["date"] != datetime.utcnow().date():
        trade_counter["count"] = 0
        trade_counter["date"] = datetime.utcnow().date()

    # Daily limit check
    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text("⚠️ Daily limit reached (5 trades)")
        return

    if query.data == "get_signal":
        best_signal = None
        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY", "SELL"]:
                if not best_signal or sig.confidence > best_signal.confidence:
                    best_signal = sig

        if not best_signal:
            await query.message.reply_text("❌ No strong signal right now")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best_signal)

# =========================
# SEND SIGNAL
# =========================
async def send_signal(query, context, sig):
    image_path = "assets/buy.png" if sig.direction == "BUY" else "assets/sell.png"

    caption = (
        f"📊 {sig.direction} SIGNAL\n\n"
        f"💱 Pair: {sig.symbol}\n"
        f"🔥 Confidence: {sig.confidence}%\n"
        f"💰 Price: {sig.price}\n"
        f"⏰ Entry: {sig.entry_time}\n"
        f"⌛ Expiry: {sig.expiry_time}\n"
        f"📡 Trend: {sig.trend}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ WIN", callback_data="win"),
            InlineKeyboardButton("❌ LOSS", callback_data="loss")
        ],
        [
            InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")
        ]
    ])

    try:
        with open(image_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img,
                caption=caption,
                reply_markup=keyboard
            )
    except Exception as e:
        await query.message.reply_text(f"⚠️ IMAGE ERROR: {str(e)}")

# =========================
# RUN BOT
# =========================
def run_bot():
    print("🚀 Bot running...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()