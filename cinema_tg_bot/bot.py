from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler
from cinema_tg_bot.config import BOT_TOKEN
from cinema_tg_bot.handlers import start, link, movies, profile, sessions, tickets
from telegram.ext import MessageHandler, filters
from cinema_tg_bot.config import EMAIL_PATTERN, CODE_PATTERN


def main():
    # Create the bot application
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start.handle_start))

    app.add_handler(MessageHandler(filters.Regex(r"^🔗 Link Account$"), link.handle_link))
    app.add_handler(MessageHandler(filters.Regex(r"^📄 My Tickets"), tickets.handle_tickets))
    app.add_handler(MessageHandler(filters.Regex(r"^👤 Profile"), profile.handle_profile))
    # app.add_handler(MessageHandler(filters.Regex(r"^🎬 Movies"), movies.handle_movies))
    # app.add_handler(MessageHandler(filters.Regex(r"^🕓 Showtimes"), sessions.handle_showtimes))

    app.add_handler(MessageHandler(filters.Regex(CODE_PATTERN) & ~filters.COMMAND,
                                   link.handle_user_code))
    app.add_handler(MessageHandler(filters.Regex(EMAIL_PATTERN) & ~filters.COMMAND,
                                   link.handle_email))
    # Start long polling (this call blocks and reconnects on failure)
    app.run_polling()

if __name__ == "__main__":
    main()
