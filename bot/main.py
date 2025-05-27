import logging
import asyncio
import os
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from bot.config import BOT_TOKEN, ADMIN_IDS
from bot.database import init_db
from bot.handlers import (
    start, help_command, generate, generatejson, settings,
    handle_settings_callback, handle_password_length,
    message_handler, admin_broadcast
)
from bot.admin_handlers import (
    register_admin_handlers, handle_broadcast_message,
    admin_menu, admin_callback, broadcast_callback
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла ошибка при обработке команды. Попробуйте позже."
        )

def run():
    """Запускает бота."""
    try:
        # Создание приложения
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавляем admin_ids в контекст бота
        application.bot_data['admin_ids'] = ADMIN_IDS

        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("generate", generate))
        application.add_handler(CommandHandler("generatejson", generatejson))
        application.add_handler(CommandHandler("settings", settings))
        application.add_handler(CommandHandler("broadcast", admin_broadcast))
        
        # Регистрация обработчика настроек
        application.add_handler(CallbackQueryHandler(
            handle_settings_callback,
            pattern='^(settings_|gender_|nat_|field_|count_|pass_)'
        ))

        # Регистрация обработчика текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Регистрация административных обработчиков
        application.add_handler(CommandHandler("admin", admin_menu))
        application.add_handler(CallbackQueryHandler(admin_callback, pattern='^(admin_stats|export_users|broadcast_message)$'))
        application.add_handler(CallbackQueryHandler(broadcast_callback, pattern='^(confirm_broadcast|cancel_broadcast)$'))
        
        # Регистрация обработчика сообщений для рассылки
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_IDS),
            handle_broadcast_message
        ))

        # Регистрация обработчика ошибок
        application.add_error_handler(error_handler)

        logger.info("Bot initialization completed successfully!")
        logger.info(f"Admin IDs: {ADMIN_IDS}")

        # Запуск бота с новыми параметрами
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            stop_signals=(signal.SIGINT, signal.SIGTERM)
        )

    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run() 