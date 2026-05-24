from telegram import Update
from telegram.ext import (
    ContextTypes,
)


async def handle_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Список фильмов: ...")
    await update.callback_query.edit_message_text("asasd: ...")
