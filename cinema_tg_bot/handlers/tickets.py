from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from cinema_tg_bot.utils.api import get_order_list



async def handle_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    ok, data = await get_order_list(tg_id)
    if not ok:
        await update.message.reply_text(f"⚠️ Failed to load orders: {data}")
        return

    items = data.get("orders", [])
    if not items:
        await update.message.reply_text("You have no orders yet.")
        return

    lines = []
    for o in items:
        lines.append(
            f"• Order #{o['id']} — {o['status']} — total: {o['total_price']}\n"
            f"  {o['movie_title']} — {o['start_time']}–{o['end_time']} — Hall: {o['hall_name']}\n"
            f"  Seats: {o['seats']}"
        )
    await update.message.reply_text("🎟 Your orders:\n" + "\n".join(lines))

