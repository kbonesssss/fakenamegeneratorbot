from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import sqlite3
import json
import logging
from typing import List, Optional
from .user_settings import UserSettings
from contextlib import contextmanager

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    
class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)

async def init_db():
    engine = create_async_engine('sqlite+aiosqlite:///bot.db')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine

async def get_session_maker(engine):
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        logger.info(f"Initializing database with file: {db_file}")
        self.create_tables()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_file, timeout=20.0)
        try:
            yield conn
        finally:
            conn.close()

    def create_tables(self):
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                
                logger.debug("Creating users table")
                c.execute('''CREATE TABLE IF NOT EXISTS users
                            (telegram_id INTEGER PRIMARY KEY, username TEXT)''')
                
                logger.debug("Creating user_settings table")
                c.execute('''CREATE TABLE IF NOT EXISTS user_settings
                            (telegram_id INTEGER PRIMARY KEY,
                             gender TEXT,
                             nationality TEXT,
                             password_settings TEXT,
                             results_count INTEGER,
                             include_fields TEXT,
                             exclude_fields TEXT,
                             FOREIGN KEY (telegram_id) REFERENCES users(telegram_id))''')
                
                logger.debug("Creating broadcast_history table")
                c.execute('''CREATE TABLE IF NOT EXISTS broadcast_history
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             admin_id INTEGER NOT NULL,
                             timestamp TEXT NOT NULL,
                             total_users INTEGER NOT NULL,
                             sent_count INTEGER NOT NULL,
                             failed_count INTEGER NOT NULL,
                             failed_users TEXT,
                             FOREIGN KEY (admin_id) REFERENCES users(telegram_id))''')
                
                conn.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def add_user(self, telegram_id: int, username: str):
        try:
            logger.info(f"Adding user to database: {telegram_id} (@{username})")
            with self.get_connection() as conn:
                c = conn.cursor()
                
                # Начинаем транзакцию
                conn.execute('BEGIN')
                try:
                    # Добавляем пользователя
                    c.execute('INSERT OR REPLACE INTO users (telegram_id, username) VALUES (?, ?)',
                             (telegram_id, username))
                    
                    # Создаем настройки по умолчанию
                    default_settings = UserSettings.get_default_settings(telegram_id)
                    
                    # Сохраняем настройки
                    c.execute('''INSERT OR REPLACE INTO user_settings 
                                (telegram_id, gender, nationality, password_settings,
                                 results_count, include_fields, exclude_fields)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (default_settings.telegram_id,
                              default_settings.gender,
                              json.dumps(default_settings.nationality) if default_settings.nationality else None,
                              default_settings.password_settings,
                              default_settings.results_count,
                              json.dumps(default_settings.include_fields) if default_settings.include_fields else None,
                              json.dumps(default_settings.exclude_fields) if default_settings.exclude_fields else None))
                    
                    # Завершаем транзакцию
                    conn.commit()
                    logger.info(f"User {telegram_id} and settings added successfully")
                except Exception as e:
                    # В случае ошибки откатываем транзакцию
                    conn.rollback()
                    raise e
                
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            raise

    def get_user_settings(self, telegram_id: int) -> Optional[UserSettings]:
        try:
            logger.debug(f"Getting settings for user: {telegram_id}")
            with self.get_connection() as conn:
                c = conn.cursor()
                
                c.execute('SELECT * FROM user_settings WHERE telegram_id = ?', (telegram_id,))
                row = c.fetchone()
                
                if not row:
                    logger.debug(f"No settings found for user {telegram_id}, creating default")
                    return UserSettings.get_default_settings(telegram_id)
                    
                settings = UserSettings(
                    telegram_id=row[0],
                    gender=row[1],
                    nationality=json.loads(row[2]) if row[2] else None,
                    password_settings=row[3],
                    results_count=row[4],
                    include_fields=json.loads(row[5]) if row[5] else None,
                    exclude_fields=json.loads(row[6]) if row[6] else None
                )
                
                return settings
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            raise

    def save_user_settings(self, settings: UserSettings):
        try:
            logger.debug(f"Saving settings for user: {settings.telegram_id}")
            with self.get_connection() as conn:
                c = conn.cursor()
                
                c.execute('''INSERT OR REPLACE INTO user_settings 
                            (telegram_id, gender, nationality, password_settings,
                             results_count, include_fields, exclude_fields)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (settings.telegram_id,
                          settings.gender,
                          json.dumps(settings.nationality) if settings.nationality else None,
                          settings.password_settings,
                          settings.results_count,
                          json.dumps(settings.include_fields) if settings.include_fields else None,
                          json.dumps(settings.exclude_fields) if settings.exclude_fields else None))
                
                conn.commit()
                logger.debug(f"Settings saved successfully for user {settings.telegram_id}")
        except Exception as e:
            logger.error(f"Error saving user settings: {str(e)}")
            raise

    def get_all_users(self) -> list:
        """Получает список всех пользователей."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                logger.info("Fetching all users from database")
                
                # Проверяем существование таблицы
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                if not c.fetchone():
                    logger.error("Users table does not exist!")
                    return []
                
                # Получаем количество пользователей
                c.execute('SELECT COUNT(*) FROM users')
                count = c.fetchone()[0]
                logger.info(f"Total users in database: {count}")
                
                # Получаем всех пользователей
                c.execute('SELECT telegram_id, username FROM users')
                users = c.fetchall()
                
                if not users:
                    logger.warning("No users found in database")
                    return []
                    
                logger.info(f"Successfully fetched {len(users)} users from database")
                return users
                
        except sqlite3.Error as e:
            logger.error(f"SQLite error in get_all_users: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_all_users: {str(e)}", exc_info=True)
            return []

    def save_broadcast_results(self, admin_id: int, timestamp: str, total_users: int,
                             sent_count: int, failed_count: int, failed_users: list) -> None:
        """Сохраняет результаты рассылки в базу данных."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO broadcast_history 
                           (admin_id, timestamp, total_users, sent_count, failed_count, failed_users)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (admin_id, timestamp, total_users, sent_count, failed_count,
                         json.dumps(failed_users) if failed_users else None))
                conn.commit()
                logger.info(f"Broadcast results saved successfully for admin {admin_id}")
        except Exception as e:
            logger.error(f"Error saving broadcast results: {str(e)}")
            raise

    def get_broadcast_history(self, limit: int = 10) -> list:
        """Получает историю рассылок."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                c.execute('''SELECT * FROM broadcast_history 
                           ORDER BY timestamp DESC LIMIT ?''', (limit,))
                return c.fetchall()
        except Exception as e:
            logger.error(f"Error getting broadcast history: {str(e)}")
            return [] 