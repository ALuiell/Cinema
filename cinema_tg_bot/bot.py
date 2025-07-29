from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers.start import handle_start


def main():
    # Create the bot application
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", handle_start))

    # Start long polling (this call blocks and reconnects on failure)
    application.run_polling()

if __name__ == "__main__":
    main()
