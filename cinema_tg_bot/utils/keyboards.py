from telegram import ReplyKeyboardMarkup

def guest_menu():
    return ReplyKeyboardMarkup(
        [["🎬 Movies", "🕓 Showtimes"], ["🔗 Link Account"]],
        resize_keyboard=True
    )

def user_menu():
    return ReplyKeyboardMarkup(
        [["🎬 Movies", "🕓 Showtimes"], ["📄 My Tickets", "👤 Profile"]],
        resize_keyboard=True
    )

# profile menu | unlinked | edit info | notification

