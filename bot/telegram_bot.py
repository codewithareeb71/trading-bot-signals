from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes
from .signal_engine import generate_signal
from .config import TELEGRAM_BOT_TOKEN
from datetime import datetime

# =========================
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# =========================
CURRENCY_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
    "USD_CAD", "NZD_USD", "EUR_GBP", "GBP_JPY", "USD_TRY"
]

MAX_TRADES_PER_DAY = 5
trade_counter = {"count": 0, "date": datetime.utcnow().date()}

# =========================
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    # User sees only GET SIGNAL button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])
    await update.message.reply_text(
        "👋 Welcome to Trading Bot\n"
        f"ℹ️ You can take {MAX_TRADES_PER_DAY} trades/day\n"
        "⏱️ Each trade 2-min execution window\n"
        "🔥 Only high-confidence signals will be sent",
        reply_markup=keyboard
    )

# =========================
async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    global trade_counter
    query = update.callback_query
    await query.answer("Processing signal... ⏳")  # instant response

    # Reset daily counter
    if trade_counter["date"] != datetime.utcnow().date():
        trade_counter["count"] = 0
        trade_counter["date"] = datetime.utcnow().date()

    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text("⚠️ Daily trade limit reached! Come back tomorrow.")
        return

    data = query.data
    if data == "get_signal":
        best_signal = None
        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol, trade_window_minutes=2)
            if sig and sig.status == "ACTIVE":
                if not best_signal or sig.confidence > best_signal.confidence:
                    best_signal = sig

        if not best_signal:
            await query.message.reply_text("❌ No strong signal right now.")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best_signal)

# =========================
async def send_signal(query, context, sig):
    image_path = "assets/buy.png" if sig.direction == "BUY" else "assets/sell.png"
    caption = (
        f"🟢 <b>{sig.direction} SIGNAL</b>\n\n"
        f"💱 Pair: {sig.symbol.replace('_','/')}\n"
        f"📊 Direction: {sig.direction}\n"
        f"🔥 Confidence: {sig.confidence}%\n"
        f"💰 Amount: {sig.price}\n"
        f"⏰ Entry: {sig.entry_time}\n"
        f"⌛ Expiry: {sig.expiry_time}\n"
        f"📡 Status: {sig.status}\n"
        f"💬 {sig.message}"
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
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        await query.message.reply_text(f"⚠️ IMAGE ERROR: {str(e)}")

# =========================
def run_bot():
    print("🚀 Bot running...")
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()