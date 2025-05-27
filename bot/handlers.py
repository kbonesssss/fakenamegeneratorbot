from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import traceback
import json
import io
from datetime import datetime

from .database import User, Settings, init_db, get_session_maker
from .keyboards import get_main_keyboard
from .utils import get_random_user, format_user_data, broadcast_message, translate_gender, format_settings
from .database import Database
from .user_settings import UserSettings, DEFAULT_SETTINGS
from .settings_keyboards import (
    get_settings_keyboard, get_gender_keyboard,
    get_nationality_keyboard, get_password_settings_keyboard,
    get_fields_keyboard, get_results_count_keyboard
)
from .admin_handlers import admin_menu

logger = logging.getLogger(__name__)

db = Database('bot.db')

async def get_session_maker_from_context(context):
    """Get or create session maker from context."""
    if 'session_maker' not in context.bot_data:
        engine = await init_db()
        session_maker = await get_session_maker(engine)
        context.bot_data['session_maker'] = session_maker
        logger.info("Database initialized")
    return context.bot_data['session_maker']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    try:
        if not update or not update.effective_user:
            logger.error("No update or user object")
            return

        user = update.effective_user
        logger.info(f"Start command from user: {user.id} (@{user.username})")
        
        # Добавляем пользователя в базу данных
        db.add_user(user.id, user.username)
        
        # Отправляем приветственное сообщение
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            "Я бот для генерации случайных пользовательских данных.\n\n"
            "🎲 Используйте команду /generate для генерации случайного пользователя\n"
            "⚙️ Для настройки параметров генерации используйте команду /settings\n"
            "❓ Для получения справки используйте команду /help",
            reply_markup=get_main_keyboard(user.id in context.bot_data.get('admin_ids', []))
        )
        logger.debug("Welcome message sent")

    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /generate."""
    user_id = update.effective_user.id
    settings = db.get_user_settings(user_id)
    
    try:
        user_data = await get_random_user(settings)
        if settings.results_count > 1:
            for user in user_data['results']:
                formatted_data = await format_user_data({'results': [user]})
                await update.message.reply_text(formatted_data, parse_mode='Markdown')
        else:
            formatted_data = await format_user_data(user_data)
            await update.message.reply_text(formatted_data, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in generate command: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка при генерации данных. Попробуйте позже."
        )

async def generatejson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /generatejson. Генерирует данные в формате JSON."""
    user_id = update.effective_user.id
    settings = db.get_user_settings(user_id)
    
    try:
        # Создаем список для хранения всех результатов
        all_results = []
        
        # Генерируем данные нужное количество раз
        for _ in range(settings.results_count):
            user_data = await get_random_user(settings)
            # Добавляем результат в общий список
            all_results.extend(user_data['results'])
        
        # Формируем итоговый JSON со всеми результатами
        json_data = json.dumps({
            'count': len(all_results),
            'results': all_results
        }, ensure_ascii=False, indent=2)
        
        # Отправляем файл
        await update.message.reply_document(
            document=io.StringIO(json_data),
            filename='user_data.json',
            caption=f"Сгенерировано пользователей: {len(all_results)}"
        )
    except Exception as e:
        logger.error(f"Error in generatejson command: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка при генерации данных. Попробуйте позже."
        )

async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in context.bot_data['admin_ids']:
        return
    
    session_maker = await get_session_maker_from_context(context)
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()
    
        users_text = "Список пользователей:\n\n"
        for user in users:
            users_text += f"ID: {user.telegram_id}\nUsername: @{user.username}\nAdmin: {'Да' if user.is_admin else 'Нет'}\n\n"
    
        await update.message.reply_text(users_text)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение всем пользователям."""
    user = update.effective_user
    logger.info(f"Admin broadcast initiated by user {user.id}")
    
    if user.id not in context.bot_data.get('admin_ids', []):
        logger.warning(f"Unauthorized broadcast attempt by user {user.id}")
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    # Если это callback query
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "Для отправки рассылки используйте команду:\n"
            "/broadcast <текст сообщения>"
        )
        return
    
    # Если это команда
    if not context.args or len(context.args) == 0:
        logger.info("Broadcast command received without message")
        await update.message.reply_text(
            "Использование: /broadcast <сообщение>"
        )
        return
    
    message = ' '.join(context.args)
    logger.info(f"Broadcasting message: {message[:50]}...")
    
    try:
        # Получаем всех пользователей через Database класс
        logger.info("Fetching users from database...")
        users = db.get_all_users()
        
        if not users:
            logger.warning("No users found in database for broadcast")
            await update.message.reply_text("ℹ️ Нет пользователей для рассылки.")
            return
            
        logger.info(f"Starting broadcast to {len(users)} users")
        await update.message.reply_text(f"📨 Начинаю рассылку {len(users)} пользователям...")
        
        failed_users = await broadcast_message(context.bot, users, message)
        
        status = "✅ Рассылка завершена\n"
        if failed_users:
            status += f"❌ Не удалось отправить сообщение {len(failed_users)} пользователям из {len(users)}"
        else:
            status += f"✅ Сообщение успешно отправлено всем пользователям ({len(users)})"
        
        # Сохраняем результаты рассылки
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            logger.info("Saving broadcast results...")
            db.save_broadcast_results(
                admin_id=user.id,
                timestamp=timestamp,
                total_users=len(users),
                sent_count=len(users) - len(failed_users),
                failed_count=len(failed_users),
                failed_users=[u[0] if isinstance(u, tuple) else u.telegram_id for u in failed_users]
            )
            status += f"\n\n📝 Результаты сохранены ({timestamp})"
            logger.info("Broadcast results saved successfully")
        except Exception as e:
            logger.error(f"Failed to save broadcast results: {str(e)}")
            status += "\n\n⚠️ Не удалось сохранить результаты рассылки"
        
        logger.info(f"Broadcast completed. Status: {status}")
        await update.message.reply_text(status)
        
    except Exception as e:
        error_msg = f"Error in broadcast: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при выполнении рассылки. "
            "Проверьте логи для получения дополнительной информации."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Доступные команды:*\n\n"
        "/generate - Генерация случайного пользователя в текстовом формате\n"
        "/generatejson - Генерация случайного пользователя в формате JSON-файла\n"
        "/settings - Настройка параметров генерации:\n"
        "   - Национальность\n"
        "   - Пол\n"
        "   - Настройки пароля\n"
        "   - Выбор полей\n"
        "   - Количество результатов\n"
        "/help - Показать это сообщение\n\n"
        "По умолчанию генерируются пользователи обоих полов "
        "из нескольких стран со стандартными полями данных.",
        parse_mode='Markdown'
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = db.get_user_settings(user_id)
    formatted_settings = format_settings(settings)
    
    # Сохраняем текущие настройки в контексте
    context.user_data['settings'] = settings.__dict__
    
    await update.message.reply_text(
        "⚙️ *Настройки генерации*\n\n"
        f"{formatted_settings}\n\n"
        "Выберите параметр для настройки:",
        reply_markup=get_settings_keyboard(context),
        parse_mode='Markdown'
    )

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    settings = db.get_user_settings(user_id)

    await query.answer()

    if data == "settings_reset":
        settings = UserSettings(user_id)
        for key, value in DEFAULT_SETTINGS.items():
            setattr(settings, key, value)
        db.save_user_settings(settings)
        context.user_data['settings'] = settings.__dict__
        formatted_settings = format_settings(settings)
        await query.message.edit_text(
            "⚙️ *Настройки генерации*\n\n"
            f"{formatted_settings}\n\n"
            "✅ Настройки сброшены к значениям по умолчанию",
            reply_markup=get_settings_keyboard(context),
            parse_mode='Markdown'
        )
    
    elif data == "settings_nationality":
        await query.message.edit_text(
            "🌍 Выберите национальности:\n"
            "(Можно выбрать несколько)\n\n"
            "Текущий выбор: " + (", ".join(settings.nationality) if settings.nationality else "Все"),
            reply_markup=get_nationality_keyboard(settings.nationality)
        )
    
    elif data == "settings_gender":
        await query.message.edit_text(
            "👥 Выберите пол:",
            reply_markup=get_gender_keyboard()
        )
    
    elif data == "settings_password":
        await query.message.edit_text(
            "🔐 Настройки пароля:\n"
            "Выберите параметры для генерации пароля",
            reply_markup=get_password_settings_keyboard()
        )
    
    elif data == "settings_fields":
        await query.message.edit_text(
            "📋 Выберите поля для включения в результат:",
            reply_markup=get_fields_keyboard(settings.include_fields)
        )
    
    elif data == "settings_count":
        await query.message.edit_text(
            "🔢 Выберите количество результатов:",
            reply_markup=get_results_count_keyboard()
        )
    
    elif data.startswith("gender_"):
        gender = data.split("_")[1]
        settings.gender = None if gender == "any" else gender
        db.save_user_settings(settings)
        formatted_settings = format_settings(settings)
        await query.message.edit_text(
            "⚙️ *Настройки генерации*\n\n"
            f"{formatted_settings}\n\n"
            f"✅ Пол успешно установлен: {translate_gender(gender) if gender != 'any' else 'Любой'}",
            reply_markup=get_settings_keyboard(context),
            parse_mode='Markdown'
        )
    
    elif data.startswith("nat_"):
        nat = data.split("_")[1]
        if settings.nationality is None:
            settings.nationality = []
        if nat in settings.nationality:
            settings.nationality.remove(nat)
        else:
            settings.nationality.append(nat)
        db.save_user_settings(settings)
        await query.message.edit_text(
            "🌍 Выберите национальности:\n"
            "(Можно выбрать несколько)\n\n"
            "Текущий выбор: " + (", ".join(settings.nationality) if settings.nationality else "Все"),
            reply_markup=get_nationality_keyboard(settings.nationality)
        )
    
    elif data.startswith("field_"):
        field = data.split("_")[1]
        if settings.include_fields is None:
            settings.include_fields = []
        if field in settings.include_fields:
            settings.include_fields.remove(field)
        else:
            settings.include_fields.append(field)
        db.save_user_settings(settings)
        await query.message.edit_text(
            "📋 Выберите поля для включения в результат:\n\n"
            f"Текущие поля: {', '.join(settings.include_fields) if settings.include_fields else 'Все'}",
            reply_markup=get_fields_keyboard(settings.include_fields)
        )
    
    elif data.startswith("count_"):
        count = int(data.split("_")[1])
        settings.results_count = count
        db.save_user_settings(settings)
        formatted_settings = format_settings(settings)
        await query.message.edit_text(
            "⚙️ *Настройки генерации*\n\n"
            f"{formatted_settings}\n\n"
            f"✅ Количество результатов установлено: {count}",
            reply_markup=get_settings_keyboard(context),
            parse_mode='Markdown'
        )
    
    elif data.startswith("pass_"):
        param = data.split("_")[1]
        if param == "length":
            context.user_data['awaiting_password_length'] = True
            await query.message.edit_text(
                "📏 Введите длину пароля в формате: min-max\n"
                "Например: 8-16\n\n"
                "Или просто число для фиксированной длины",
                reply_markup=None
            )
        else:
            current_settings = settings.password_settings.split(",") if settings.password_settings else []
            if param in current_settings:
                current_settings.remove(param)
            else:
                current_settings.append(param)
            settings.password_settings = ",".join(current_settings) if current_settings else None
            db.save_user_settings(settings)
            
            # Форматируем текущие настройки для отображения
            display_settings = []
            for setting in current_settings:
                if setting == "lower":
                    display_settings.append("строчные буквы")
                elif setting == "upper":
                    display_settings.append("прописные буквы")
                elif setting == "number":
                    display_settings.append("цифры")
                elif setting == "special":
                    display_settings.append("спецсимволы")
                elif "-" in setting:
                    min_len, max_len = setting.split("-")
                    display_settings.append(f"длина {min_len}-{max_len}")
                elif setting.isdigit():
                    display_settings.append(f"длина {setting}")
            
            current_settings_text = ", ".join(display_settings) if display_settings else "не выбраны"
            
            await query.message.edit_text(
                "🔐 Настройки пароля:\n\n"
                f"Текущие настройки: {current_settings_text}\n\n"
                "Выберите параметры для генерации пароля:",
                reply_markup=get_password_settings_keyboard()
            )
    
    elif data == "settings_back":
        formatted_settings = format_settings(settings)
        await query.message.edit_text(
            "⚙️ *Настройки генерации*\n\n"
            f"{formatted_settings}\n\n"
            "Выберите параметр для настройки:",
            reply_markup=get_settings_keyboard(context),
            parse_mode='Markdown'
        )
    
    elif data == "settings_save":
        await query.message.edit_text(
            "✅ Настройки сохранены!\n\n"
            "Используйте /generate для генерации случайного пользователя "
            "с новыми настройками."
        )

async def handle_password_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'awaiting_password_length' not in context.user_data:
        return

    text = update.message.text
    user_id = update.effective_user.id
    settings = db.get_user_settings(user_id)
    
    try:
        if '-' in text:
            min_len, max_len = map(int, text.split('-'))
            if min_len > max_len:
                min_len, max_len = max_len, min_len
            if min_len < 1:
                min_len = 1
            if max_len > 128:
                max_len = 128
            length_setting = f"{min_len}-{max_len}"
        else:
            length = int(text)
            if length < 1:
                length = 1
            if length > 128:
                length = 128
            length_setting = str(length)
        
        # Получаем текущие настройки или создаем новые
        current_settings = []
        if settings.password_settings:
            # Удаляем старые настройки длины, сохраняем остальные настройки
            current_settings = [s for s in settings.password_settings.split(",") 
                              if not (s.isdigit() or '-' in s)]
        
        # Если нет настроек символов, добавляем базовые
        if not any(s in ["lower", "upper", "number", "special"] for s in current_settings):
            current_settings.extend(["lower", "upper", "number"])
        
        # Добавляем новую настройку длины
        current_settings.append(length_setting)
        settings.password_settings = ",".join(current_settings)
        
        db.save_user_settings(settings)
        
        # Форматируем сообщение об успехе
        if '-' in length_setting:
            min_len, max_len = length_setting.split('-')
            success_msg = f"✅ Длина пароля установлена: от {min_len} до {max_len} символов"
        else:
            success_msg = f"✅ Длина пароля установлена: {length_setting} символов"
        
        await update.message.reply_text(
            f"{success_msg}\n\n"
            "Вернуться в настройки: /settings"
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введите число или диапазон (например: 8-16)\n"
            "Минимальная длина: 1, максимальная: 128"
        )
    
    del context.user_data['awaiting_password_length']

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if text == "⚙️ Настройки":
        await settings(update, context)
    elif text == "👥 Список пользователей":
        await admin_users_list(update, context)
    elif text == "📢 Рассылка сообщений":
        await admin_broadcast(update, context)
    elif text == "🔧 Админ-панель":
        await admin_menu(update, context)
    elif context.user_data.get('awaiting_password_length'):
        await handle_password_length(update, context) 