import aiohttp
import ssl
import logging
import random
import asyncio
from typing import Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from .user_settings import UserSettings
from .user_generator import UserGenerator

logger = logging.getLogger(__name__)

def translate_gender(gender):
    return "Женский" if gender == "female" else "Мужской"

def escape_markdown(text):
    """Экранирует специальные символы Markdown."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def get_random_user(settings: UserSettings = None) -> Dict[str, Any]:
    """Генерирует случайного пользователя с учетом настроек."""
    try:
        if settings is None:
            settings = UserSettings.get_default_settings(0)

        # Определяем национальность
        nationality = random.choice(settings.nationality) if settings.nationality else random.choice(UserGenerator.get_available_countries())

        # Генерируем пользователя
        user_data = UserGenerator.generate_user(
            country_code=nationality,
            gender=settings.gender,
            password_settings=settings.password_settings
        )

        # Форматируем данные в нужный формат
        formatted_data = {
            "results": [{
                "name": {
                    "first": user_data.get("first_name", ""),
                    "last": user_data.get("last_name", "")
                },
                "gender": user_data.get("gender", ""),
                "location": {
                    "street": {
                        "name": user_data.get("address", "").split(",")[0] if "," in user_data.get("address", "") else "",
                        "number": ""
                    },
                    "city": user_data.get("address", "").split(",")[1].strip() if "," in user_data.get("address", "") else "",
                    "country": user_data.get("country", "")
                },
                "email": user_data.get("email", ""),
                "login": user_data.get("login", {}),
                "phone": user_data.get("phone", ""),
                "cell": user_data.get("phone", ""),
                "dob": {
                    "date": user_data.get("birth_date", ""),
                    "age": user_data.get("age", 0)
                },
                "physical": user_data.get("physical", {}),
                "education": user_data.get("education", {}),
                "occupation": user_data.get("occupation", ""),
                "languages": user_data.get("languages", []),
                "hobbies": user_data.get("hobbies", []),
                "marital_status": user_data.get("marital_status", ""),
                "social_media": user_data.get("social_media", {})
            }]
        }
        
        return formatted_data
    except Exception as e:
        logger.error(f"Error in get_random_user: {str(e)}")
        raise

async def format_user_data(user_data):
    user = user_data['results'][0]
    
    # Базовая информация (всегда включена)
    formatted_data = []
    
    if 'name' in user:
        name = f"{user['name']['first']} {user['name']['last']}"
        name_data = [
            "👤 *Личные данные:*",
            f"ФИО: `{name}`"
        ]
        if 'gender' in user:
            name_data.append(f"Пол: `{translate_gender(user['gender'])}`")
        if 'dob' in user:
            name_data.append(f"Возраст: `{user['dob']['age']} лет`")
            if 'date' in user['dob']:
                birth_date = user['dob']['date'].split('T')[0] if 'T' in user['dob']['date'] else user['dob']['date']
                name_data.append(f"Дата рождения: `{birth_date}`")
        formatted_data.append('\n'.join(name_data))
    
    # Физические данные
    if 'physical' in user:
        physical_data = [
            "💪 *Физические данные:*",
            f"Рост: `{user['physical']['height']} см`",
            f"Вес: `{user['physical']['weight']} кг`",
            f"Группа крови: `{user['physical']['blood_type']}`"
        ]
        formatted_data.append('\n'.join(physical_data))

    # Адрес (если включен)
    if 'location' in user:
        location_data = [
            "📍 *Адрес:*",
            f"Страна: `{user['location']['country']}`",
            f"Город: `{user['location']['city']}`",
            f"Улица: `{user['location']['street']['name']}`"
        ]
        formatted_data.append('\n'.join(location_data))
    
    # Образование
    if 'education' in user:
        education_data = [
            "🎓 *Образование:*",
            f"Уровень: `{user['education']['level']}`",
            f"Университет: `{user['education']['university']}`",
            f"Год выпуска: `{user['education']['graduation_year']}`"
        ]
        formatted_data.append('\n'.join(education_data))

    # Работа
    if 'occupation' in user:
        occupation_data = [
            "💼 *Работа:*",
            f"Профессия: `{user['occupation']}`"
        ]
        formatted_data.append('\n'.join(occupation_data))

    # Языки и хобби
    languages_hobbies_data = []
    if 'languages' in user:
        languages_str = "`, `".join(user['languages'])
        languages_hobbies_data.append(f"Языки: `{languages_str}`")
    if 'hobbies' in user:
        hobbies_str = "`, `".join(user['hobbies'])
        languages_hobbies_data.append(f"Хобби: `{hobbies_str}`")
    if languages_hobbies_data:
        formatted_data.append("🌍 *Языки и интересы:*\n" + "\n".join(languages_hobbies_data))

    # Семейное положение
    if 'marital_status' in user:
        marital_data = [
            "💑 *Семейное положение:*",
            f"Статус: `{user['marital_status']}`"
        ]
        formatted_data.append('\n'.join(marital_data))

    # Контактная информация (если включена)
    contact_data = []
    if any(key in user for key in ['email', 'phone', 'cell']):
        contact_data.append("📱 *Контактная информация:*")
        if 'email' in user:
            contact_data.append(f"Email: `{user['email']}`")
        if 'phone' in user:
            contact_data.append(f"Телефон: `{user['phone']}`")
        if 'cell' in user:
            contact_data.append(f"Мобильный: `{user['cell']}`")
        formatted_data.append('\n'.join(contact_data))
    
    # Социальные сети
    if 'social_media' in user:
        social_data = ["🌐 *Социальные сети:*"]
        for platform, username in user['social_media'].items():
            social_data.append(f"{platform}: `{username}`")
        formatted_data.append('\n'.join(social_data))

    # Данные для входа (если включены)
    if 'login' in user:
        login_data = [
            "🔐 *Данные для входа:*",
            f"Логин: `{user['login']['username']}`",
            f"Пароль: `{user['login']['password']}`"
        ]
        formatted_data.append('\n'.join(login_data))
    
    # Объединяем все секции
    return '\n\n'.join(formatted_data)

async def check_subscription(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except TelegramError:
        return False

async def broadcast_message(bot: Bot, users, message: str):
    failed_users = []
    logger.info(f"Starting broadcast to {len(users) if users else 0} users")
    
    if not users:
        logger.warning("No users to broadcast to!")
        return failed_users
        
    for i, user in enumerate(users, 1):
        try:
            # Получаем telegram_id в зависимости от типа user
            telegram_id = user.telegram_id if hasattr(user, 'telegram_id') else user[0]
            logger.info(f"Sending message to user {telegram_id} ({i}/{len(users)})")
            
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'  # Добавляем поддержку Markdown
            )
            logger.info(f"Successfully sent message to user {telegram_id}")
            await asyncio.sleep(0.05)  # Добавляем небольшую задержку
            
        except TelegramError as e:
            logger.error(f"Telegram error while sending to user {telegram_id}: {str(e)}")
            failed_users.append(user)
        except Exception as e:
            logger.error(f"Unexpected error while sending to user {telegram_id}: {str(e)}")
            failed_users.append(user)
            
    logger.info(f"Broadcast completed. Failed: {len(failed_users)}/{len(users)}")
    return failed_users

def format_settings(settings):
    """Форматирует настройки для отображения пользователю."""
    formatted = []
    
    # Национальность
    nations = ", ".join(settings.nationality) if settings.nationality else "Все"
    formatted.append(f"🌍 *Национальность:* {nations}")
    
    # Пол
    gender = translate_gender(settings.gender) if settings.gender else "Любой"
    formatted.append(f"👥 *Пол:* {gender}")
    
    # Поля данных
    fields = ", ".join(settings.include_fields) if settings.include_fields else "Все"
    formatted.append(f"📋 *Поля данных:* {fields}")
    
    # Количество результатов
    formatted.append(f"🔢 *Количество результатов:* {settings.results_count}")
    
    # Настройки пароля
    if settings.password_settings:
        pass_settings = []
        for setting in settings.password_settings.split(","):
            if setting == "lower":
                pass_settings.append("строчные")
            elif setting == "upper":
                pass_settings.append("прописные")
            elif setting == "number":
                pass_settings.append("цифры")
            elif setting == "special":
                pass_settings.append("спецсимволы")
            elif "-" in setting:
                min_len, max_len = setting.split("-")
                pass_settings.append(f"длина {min_len}-{max_len}")
            else:
                try:
                    length = int(setting)
                    pass_settings.append(f"длина {length}")
                except ValueError:
                    pass
        formatted.append(f"🔐 *Пароль:* {', '.join(pass_settings)}")
    else:
        formatted.append("🔐 *Пароль:* стандартные настройки")
    
    return "\n".join(formatted) 