from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .user_settings import AVAILABLE_NATIONALITIES, AVAILABLE_FIELDS, PASSWORD_CHARSETS

def get_settings_keyboard(context=None):
    keyboard = [
        [
            InlineKeyboardButton("🌍 Национальность", callback_data="settings_nationality"),
            InlineKeyboardButton("👥 Пол", callback_data="settings_gender")
        ],
        [
            InlineKeyboardButton("🔐 Пароль", callback_data="settings_password"),
            InlineKeyboardButton("📋 Поля", callback_data="settings_fields")
        ],
        [InlineKeyboardButton("🔢 Количество результатов", callback_data="settings_count")],
        [
            InlineKeyboardButton("✅ Сохранить", callback_data="settings_save"),
            InlineKeyboardButton("🔄 Сбросить", callback_data="settings_reset")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def is_preset_active(preset_settings, current_settings):
    """Проверяет, соответствуют ли текущие настройки пресету"""
    if not current_settings:
        return False
    
    for key, value in preset_settings.items():
        if key not in current_settings:
            return False
            
        current_value = current_settings[key]
        
        # Обработка списков
        if isinstance(value, list) and isinstance(current_value, list):
            if sorted(value) != sorted(current_value):
                return False
        # Обработка None
        elif value is None and current_value is None:
            continue
        # Обработка строк с настройками пароля
        elif key == 'password_settings' and value and current_value:
            preset_parts = set(value.split(','))
            current_parts = set(current_value.split(','))
            if preset_parts != current_parts:
                return False
        # Обычное сравнение
        elif value != current_value:
            return False
    
    return True

def get_presets_keyboard():
    keyboard = []
    for preset_id, preset_data in PRESETS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{preset_data['name']} - {preset_data['description']}", 
                callback_data=f"preset_{preset_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")])
    return InlineKeyboardMarkup(keyboard)

def get_gender_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👨 Мужской", callback_data="gender_male"),
            InlineKeyboardButton("👩 Женский", callback_data="gender_female")
        ],
        [InlineKeyboardButton("🔄 Любой", callback_data="gender_any")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_nationality_keyboard(selected_nations=None):
    if selected_nations is None:
        selected_nations = []
    
    keyboard = []
    row = []
    
    for nat in AVAILABLE_NATIONALITIES:
        mark = "✅" if nat in selected_nations else "⬜️"
        row.append(InlineKeyboardButton(
            f"{mark} {nat}",
            callback_data=f"nat_{nat}"
        ))
        
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")])
    return InlineKeyboardMarkup(keyboard)

def get_password_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔡 Строчные", callback_data="pass_lower"),
            InlineKeyboardButton("🔠 Прописные", callback_data="pass_upper")
        ],
        [
            InlineKeyboardButton("🔢 Цифры", callback_data="pass_number"),
            InlineKeyboardButton("❗️ Спецсимволы", callback_data="pass_special")
        ],
        [InlineKeyboardButton("📏 Длина пароля", callback_data="pass_length")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_fields_keyboard(include_fields=None):
    if include_fields is None:
        include_fields = []
    
    keyboard = []
    row = []
    
    for field in AVAILABLE_FIELDS:
        mark = "✅" if field in include_fields else "⬜️"
        row.append(InlineKeyboardButton(
            f"{mark} {field}",
            callback_data=f"field_{field}"
        ))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")])
    return InlineKeyboardMarkup(keyboard)

def get_results_count_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="count_1"),
            InlineKeyboardButton("5", callback_data="count_5"),
            InlineKeyboardButton("10", callback_data="count_10")
        ],
        [
            InlineKeyboardButton("25", callback_data="count_25"),
            InlineKeyboardButton("50", callback_data="count_50"),
            InlineKeyboardButton("100", callback_data="count_100")
        ],
        [InlineKeyboardButton("⬅️ Назад", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(keyboard) 