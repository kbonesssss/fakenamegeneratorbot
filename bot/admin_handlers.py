from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import csv
import io
from datetime import datetime
import logging
import asyncio
from typing import Optional, Dict
from .database import Database
from .config import ADMIN_IDS

logger = logging.getLogger(__name__)
db = Database('bot.db')

# Словарь для хранения активных рассылок
active_broadcasts: Dict[int, bool] = {}

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает административное меню."""
    user_id = update.effective_user.id
    logger.info(f"Admin menu accessed by user {user_id}. Admin IDs: {ADMIN_IDS}")
    
    if user_id not in ADMIN_IDS:
        logger.warning(f"Access denied for user {user_id}")
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Статистика пользователей", callback_data='admin_stats')],
        [InlineKeyboardButton("📤 Выгрузить пользователей (CSV)", callback_data='export_users')],
        [InlineKeyboardButton("📨 Создать рассылку", callback_data='broadcast_message')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔧 *Панель администратора*\nВыберите действие:", reply_markup=reply_markup, parse_mode='Markdown')

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопок административного меню."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await query.answer("У вас нет доступа к этой команде.", show_alert=True)
        return
        
    logger.info(f"Admin callback received: {query.data} from user {user_id}")
    await query.answer()

    if query.data == 'admin_stats':
        try:
            users = db.get_all_users()
            users_count = len(users)
            logger.info(f"Got users count: {users_count}")
            
            stats_text = (
                "*📊 Статистика бота:*\n"
                f"Всего пользователей: `{users_count}`\n"
            )
            await query.edit_message_text(stats_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ Произошла ошибка при получении статистики.",
                parse_mode='Markdown'
            )

    elif query.data == 'export_users':
        try:
            users = db.get_all_users()
            logger.info(f"Exporting {len(users)} users")
            
            if not users:
                await query.edit_message_text("ℹ️ Нет данных для экспорта: список пользователей пуст.")
                return

            # Создаем CSV файл в памяти
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Username'])
            
            for user in users:
                writer.writerow([user[0], user[1]])
            
            output.seek(0)
            file_content = output.getvalue().encode()
            output.close()
            
            filename = f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            logger.info(f"Sending CSV file: {filename}")
            
            # Отправляем файл
            await context.bot.send_document(
                chat_id=user_id,
                document=io.BytesIO(file_content),
                filename=filename,
                caption="📊 Экспорт пользователей"
            )
            
            # Подтверждаем успешный экспорт
            await query.edit_message_text("✅ Файл с данными пользователей сгенерирован и отправлен.")
        except Exception as e:
            logger.error(f"Error exporting users: {e}", exc_info=True)
            await query.edit_message_text("❌ Произошла ошибка при экспорте пользователей.")

    elif query.data == 'broadcast_message':
        try:
            context.user_data['waiting_for_broadcast'] = True
            await query.edit_message_text(
                "*📨 Создание рассылки*\n"
                "Отправьте сообщение, которое нужно разослать всем пользователям.\n"
                "Поддерживается форматирование Markdown.\n\n"
                "Для отмены используйте команду /cancel",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error starting broadcast: {e}", exc_info=True)
            await query.edit_message_text("❌ Произошла ошибка при создании рассылки.")

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщение для рассылки."""
    user_id = update.effective_user.id
    
    if not context.user_data.get('waiting_for_broadcast'):
        logger.debug(f"Ignoring message from {user_id}: not waiting for broadcast")
        return

    if user_id not in ADMIN_IDS:
        logger.warning(f"Access denied for user {user_id}")
        return

    try:
        context.user_data['waiting_for_broadcast'] = False
        message_text = update.message.text
        logger.info(f"Received broadcast message from admin {user_id}: {message_text[:50]}...")
        
        # Сохраняем сообщение в context.user_data
        context.user_data['broadcast_message'] = {
            'text': message_text,
            'parse_mode': 'Markdown'
        }

        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data='confirm_broadcast'),
                InlineKeyboardButton("❌ Отменить", callback_data='cancel_broadcast')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        preview_text = (
            "*📨 Предпросмотр рассылки:*\n\n"
            f"{message_text}\n\n"
            "Выберите действие:"
        )
        
        await update.message.reply_text(preview_text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error handling broadcast message: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при создании рассылки.")
        context.user_data['waiting_for_broadcast'] = False

async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает подтверждение или отмену рассылки."""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await query.answer("У вас нет доступа к этой команде.", show_alert=True)
        return
        
    logger.info(f"Broadcast callback received: {query.data} from user {user_id}")
    await query.answer()

    if query.data == 'cancel_broadcast':
        await query.edit_message_text("❌ Рассылка отменена.")
        return

    if query.data == 'confirm_broadcast':
        try:
            broadcast_data = context.user_data.get('broadcast_message')
            if not broadcast_data:
                logger.error("No broadcast message found in context")
                await query.edit_message_text("❌ Ошибка: сообщение для рассылки не найдено.")
                return
            
            # Получаем всех пользователей
            users = db.get_all_users()
            if not users:
                await query.edit_message_text("ℹ️ Нет пользователей для рассылки.")
                return

            total_users = len(users)
            sent_count = 0
            failed_count = 0
            failed_users = []

            logger.info(f"Starting broadcast to {total_users} users")
            
            # Устанавливаем флаг активной рассылки
            active_broadcasts[user_id] = True

            status_message = await query.message.reply_text(
                "📨 Выполняется рассылка...\n"
                f"Прогресс: 0/{total_users}\n\n"
                "Для отмены используйте команду /cancel_broadcast"
            )

            batch_size = 25  # Размер пакета для обновления статуса
            last_update_time = datetime.now()

            for i, user in enumerate(users, 1):
                # Проверяем, не была ли отменена рассылка
                if not active_broadcasts.get(user_id):
                    logger.info("Broadcast was cancelled by admin")
                    await status_message.edit_text("🛑 Рассылка прервана администратором.")
                    return

                try:
                    await context.bot.send_message(
                        chat_id=user[0],  # telegram_id
                        text=broadcast_data['text'],
                        parse_mode=broadcast_data['parse_mode']
                    )
                    sent_count += 1
                    logger.debug(f"Message sent to user {user[0]}")
                    # Добавляем задержку между отправками
                    await asyncio.sleep(0.05)  # 50ms между сообщениями
                except Exception as e:
                    failed_count += 1
                    failed_users.append(user[0])
                    logger.error(f"Failed to send broadcast to user {user[0]}: {str(e)}")

                # Обновляем статус каждые batch_size сообщений или каждые 3 секунды
                current_time = datetime.now()
                if i % batch_size == 0 or (current_time - last_update_time).seconds >= 3:
                    try:
                        await status_message.edit_text(
                            "📨 Выполняется рассылка...\n"
                            f"Прогресс: {i}/{total_users}\n"
                            f"✅ Отправлено: {sent_count}\n"
                            f"❌ Ошибок: {failed_count}"
                        )
                        last_update_time = current_time
                    except Exception as e:
                        logger.error(f"Failed to update status message: {str(e)}")

            # Удаляем флаг активной рассылки
            active_broadcasts.pop(user_id, None)

            # Сохраняем результаты рассылки
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                db.save_broadcast_results(
                    admin_id=user_id,
                    timestamp=timestamp,
                    total_users=total_users,
                    sent_count=sent_count,
                    failed_count=failed_count,
                    failed_users=failed_users
                )
                logger.info(f"Broadcast results saved: sent={sent_count}, failed={failed_count}")
            except Exception as e:
                logger.error(f"Failed to save broadcast results: {str(e)}")

            result_text = (
                "✅ Рассылка завершена\n\n"
                f"📊 Статистика:\n"
                f"- Всего пользователей: {total_users}\n"
                f"- Успешно отправлено: {sent_count}\n"
                f"- Ошибок отправки: {failed_count}\n\n"
                f"📝 Результаты сохранены ({timestamp})"
            )
            await status_message.edit_text(result_text)
        except Exception as e:
            logger.error(f"Error during broadcast: {e}", exc_info=True)
            await query.message.reply_text("❌ Произошла ошибка при выполнении рассылки.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отменяет текущую операцию."""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return

    if context.user_data.get('waiting_for_broadcast'):
        context.user_data['waiting_for_broadcast'] = False
        logger.info(f"Broadcast creation cancelled by admin {user_id}")
        await update.message.reply_text("❌ Создание рассылки отменено.")

async def cancel_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отменяет текущую рассылку."""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return

    if user_id in active_broadcasts:
        active_broadcasts[user_id] = False
        logger.info(f"Active broadcast cancelled by admin {user_id}")
        await update.message.reply_text("🛑 Отмена рассылки...")
    else:
        await update.message.reply_text("❌ Нет активной рассылки для отмены.")

def register_admin_handlers(application):
    """Регистрирует обработчики административных команд."""
    application.add_handler(CommandHandler("admin", admin_menu))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern='^(admin_stats|export_users|broadcast_message)$'))
    application.add_handler(CallbackQueryHandler(broadcast_callback, pattern='^(confirm_broadcast|cancel_broadcast)$'))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("cancel_broadcast", cancel_broadcast_command)) 