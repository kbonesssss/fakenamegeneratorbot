from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserSettings:
    telegram_id: int
    gender: Optional[str] = None  # male/female/None
    nationality: Optional[List[str]] = None
    password_settings: Optional[str] = None
    results_count: int = 1
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    output_format: str = "text"  # text/json/xml/csv

    @staticmethod
    def get_default_settings(telegram_id: int) -> 'UserSettings':
        return UserSettings(
            telegram_id=telegram_id,
            nationality=["US", "GB", "FR", "DE"],
            include_fields=["gender", "name", "location", "email", "login", "dob", "phone", "cell", "picture"],
            results_count=1,
            output_format="text"
        )

AVAILABLE_NATIONALITIES = [
    "RU", "US", "GB", "DE", "FR"
]

AVAILABLE_FIELDS = [
    "first_name", "last_name", "gender", "name", "location", "email", 
    "login", "registered", "dob", "phone", "cell", "id", "picture", 
    "nat", "address", "birth_date", "social_media", "hobbies"
]

PASSWORD_CHARSETS = {
    "special": "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~",
    "upper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "lower": "abcdefghijklmnopqrstuvwxyz",
    "number": "0123456789"
}

DEFAULT_SETTINGS = {
    "nationality": None,  # None означает все национальности
    "gender": None,      # None означает любой пол
    "include_fields": None,  # None означает все поля
    "results_count": 1,
    "password_settings": "8-12,lower,upper,number"  # Стандартные настройки пароля
} 