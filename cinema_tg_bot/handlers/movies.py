from telegram import Update
from telegram.ext import (
    ContextTypes,
)


async def handle_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # здесь можно вызвать API и вернуть список фильмов
    await update.callback_query.edit_message_text("Список фильмов: ...")
