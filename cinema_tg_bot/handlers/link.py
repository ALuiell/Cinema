import re
from telegram import Update
from telegram.ext import ContextTypes
from cinema_tg_bot.utils.api import request_link_code, confirm_telegram_link
from cinema_tg_bot.utils.keyboards import user_menu, guest_menu
from cinema_tg_bot.config import EMAIL_PATTERN



async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User pressed the "Link Account" button
    await update.message.reply_text("🔗 To link your account, please enter your email:")
    context.user_data.clear()
    context.user_data["awaiting_email"] = True

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only handle if we are awaiting an email
    print('handle_email work')
    if not context.user_data.get("awaiting_email"):
        return
    email = update.message.text.strip()
    # Validate email format
    if not re.fullmatch(EMAIL_PATTERN, email):
        await update.message.reply_text(
            "❌ Invalid email format. Please try again."
        )
        return
    # Request backend to generate and send the link code to the email
    success, msg = await request_link_code(email)
    if not success:
        await update.message.reply_text(f"⚠️ {msg}")
        return
    # Switch to awaiting code state
    context.user_data["awaiting_email"] = False
    context.user_data["awaiting_code"] = True
    await update.message.reply_text(
        "✅ Code sent! Please enter it to complete linking:"
    )
    return

async def handle_user_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only handle if we are awaiting the code
    print("🔥 handle_user_code called; state:", context.user_data)
    if not context.user_data.get("awaiting_code"):
        return
    code = update.message.text.strip()
    tg_id = update.effective_user.id
    # Attempt to confirm the code with the backend
    success, msg = await confirm_telegram_link(code, tg_id)
    # Clear the awaiting_code flag
    context.user_data.pop("awaiting_code", None)
    if success:
        context.user_data["is_linked"] = True
        await update.message.reply_text(msg, reply_markup=user_menu())
    else:
        context.user_data["is_linked"] = False
        await update.message.reply_text(msg, reply_markup=guest_menu())
