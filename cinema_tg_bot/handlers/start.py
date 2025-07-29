from telegram import Update
from telegram.ext import ContextTypes
from cinema_tg_bot.utils.api import confirm_telegram_link, check_telegram_link
from cinema_tg_bot.utils.keyboards import guest_menu, user_menu


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    args = context.args

    # Case 1: deep link with a code
    if args:
        code = args[0]
        success, msg = await confirm_telegram_link(code, tg_id)

        if success:
            context.user_data["is_linked"] = True  # cache auth state
            await update.message.reply_text(msg, reply_markup=user_menu())
        else:
            context.user_data["is_linked"] = False
            await update.message.reply_text(msg, reply_markup=guest_menu())
        return

    # Case 2: regular /start — check auth status
    is_linked = await check_telegram_link(tg_id)
    context.user_data["is_linked"] = is_linked

    if is_linked:
        await update.message.reply_text(
            "👋 Welcome back!",
            reply_markup=user_menu()
        )
    else:
        await update.message.reply_text(
            "👋 Welcome! To access your personal data, please link your account.",
            reply_markup=guest_menu()
        )