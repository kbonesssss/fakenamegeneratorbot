import random
import string
from typing import List, Optional

from .user_settings import PASSWORD_CHARSETS

def parse_password_settings(settings_str: Optional[str]) -> tuple[List[str], int, int]:
    """
    Парсит строку настроек пароля и возвращает список наборов символов и диапазон длины.
    
    Args:
        settings_str: Строка настроек в формате "8-12,lower,upper,number"
                     или "12,lower,upper,number" для фиксированной длины
    
    Returns:
        Tuple[List[str], int, int]: (наборы символов, мин. длина, макс. длина)
    """
    if not settings_str:
        # Значения по умолчанию
        return ["lower", "upper", "number"], 8, 12
        
    parts = settings_str.split(",")
    charsets = []
    min_length = max_length = 8  # значения по умолчанию
    
    for part in parts:
        if "-" in part:  # диапазон длины
            try:
                min_str, max_str = part.split("-")
                min_length = int(min_str)
                max_length = int(max_str)
            except (ValueError, TypeError):
                min_length = max_length = 8
        elif part.isdigit():  # фиксированная длина
            min_length = max_length = int(part)
        elif part in PASSWORD_CHARSETS:  # набор символов
            charsets.append(part)
    
    if not charsets:  # если не указаны наборы символов
        charsets = ["lower", "upper", "number"]
        
    return charsets, min_length, max_length

def generate_password(settings_str: Optional[str] = None) -> str:
    """
    Генерирует пароль согласно настройкам.
    
    Args:
        settings_str: Строка настроек в формате "8-12,lower,upper,number"
                     или None для использования настроек по умолчанию
    
    Returns:
        str: Сгенерированный пароль
    """
    charsets, min_length, max_length = parse_password_settings(settings_str)
    
    # Собираем все доступные символы из выбранных наборов
    available_chars = ""
    for charset in charsets:
        available_chars += PASSWORD_CHARSETS[charset]
    
    if not available_chars:  # если почему-то нет символов
        available_chars = string.ascii_letters + string.digits
    
    # Определяем длину пароля
    password_length = random.randint(min_length, max_length)
    
    # Генерируем пароль
    password = ""
    
    # Сначала добавляем как минимум один символ из каждого набора
    for charset in charsets:
        password += random.choice(PASSWORD_CHARSETS[charset])
    
    # Добавляем оставшиеся символы
    remaining_length = password_length - len(password)
    password += ''.join(random.choice(available_chars) for _ in range(remaining_length))
    
    # Перемешиваем символы в пароле
    password_list = list(password)
    random.shuffle(password_list)
    
    return ''.join(password_list) 