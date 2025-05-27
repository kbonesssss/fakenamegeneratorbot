from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton("⚙️ Настройки")]
    ]
    if is_admin:
        keyboard.extend([
            [KeyboardButton("👥 Список пользователей")],
            [KeyboardButton("📢 Рассылка сообщений")],
            [KeyboardButton("🔧 Админ-панель")]
        ])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_check_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("Проверить подписку ✅", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("Изменить канал", callback_data="change_channel")],
        [InlineKeyboardButton("Назад", callback_data="back_to_admin")]
    ]
    return InlineKeyboardMarkup(keyboard) 