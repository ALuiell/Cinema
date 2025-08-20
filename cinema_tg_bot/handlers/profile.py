from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from cinema_tg_bot.utils.api import user_profile_info


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    ok, data = await user_profile_info(tg_id)
    if not ok:
        await update.message.reply_text(f"⚠️ Failed to load profile info: {data}")
        return

    lines = [
        f'first_name: {data["first_name"]}',
        f'last_name: {data["last_name"]}',
        f'email: {data["email"]}',
        f'edit-link: {data["edit_link"]}',
    ]

    await update.message.reply_text("🎟 Your profile info:\n" + "\n".join(lines))
