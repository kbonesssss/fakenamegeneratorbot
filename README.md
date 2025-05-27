# 🤖 Fake Name Generator Bot

Telegram бот для генерации случайных пользовательских данных с поддержкой нескольких национальностей и форматов вывода.

## 📋 Возможности

### Основные команды
- `/start` - Начало работы с ботом
- `/generate` - Генерация случайного пользователя в текстовом формате
- `/generatejson` - Генерация случайного пользователя в формате JSON-файла
- `/settings` - Настройка параметров генерации
- `/help` - Справка по командам

### Поддерживаемые страны
- 🇷🇺 Россия (RU)
- 🇺🇸 США (US)
- 🇬🇧 Великобритания (GB)
- 🇩🇪 Германия (DE)
- 🇫🇷 Франция (FR)

### Генерируемые данные
- 👤 Личные данные (имя, фамилия, пол)
- 📍 Адрес и местоположение
- 📧 Контактная информация (email, телефон)
- 🎂 Дата рождения и возраст
- 💪 Физические данные
- 🎓 Образование
- 💼 Профессия
- 🌍 Языки
- 🎨 Хобби
- 💑 Семейное положение
- 🌐 Социальные сети
- 🔐 Данные для входа (логин/пароль)

### Форматы вывода
- TEXT (по умолчанию) - форматированный текст с эмодзи
- JSON - структурированные данные

### Настройки генерации
- Выбор национальности
- Выбор пола
- Настройка формата вывода
- Количество генерируемых результатов
- Настройка параметров пароля
- Выбор включаемых полей данных

## 🚀 Установка

### Требования
- Python 3.8+
- pip
- virtualenv
- Git (опционально)

### Установка на Ubuntu сервер

1. **Подготовка сервера**
```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git
```

2. **Создание пользователя и настройка директории**
```bash
# Создаем пользователя для бота (опционально)
sudo useradd -m -s /bin/bash botuser
sudo su - botuser

# Создаем директорию для проекта
mkdir ~/fakenamegeneratorbot
cd ~/fakenamegeneratorbot
```

3. **Настройка виртуального окружения и установка зависимостей**
```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Клонируем репозиторий (если используется Git)
git clone https://github.com/your-repo/fakenamegeneratorbot.git .

# Устанавливаем зависимости
pip install -r requirements.txt
```

4. **Настройка токена бота**
```bash
# Добавляем BOT_TOKEN в активационный скрипт виртуального окружения
echo 'export BOT_TOKEN="YOUR_BOT_TOKEN"' >> venv/bin/activate

# Перезагружаем виртуальное окружение
deactivate && source venv/bin/activate
```

5. **Создание systemd сервиса**
```bash
sudo tee /etc/systemd/system/telegrambot.service << EOL
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/fakenamegeneratorbot
Environment=PYTHONPATH=/home/botuser/fakenamegeneratorbot
ExecStart=/home/botuser/fakenamegeneratorbot/venv/bin/python3 -m bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL
```

6. **Запуск бота**
```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable telegrambot

# Запускаем сервис
sudo systemctl start telegrambot

# Проверяем статус
sudo systemctl status telegrambot
```

## 📝 Использование

1. **Начало работы**
   - Найдите бота в Telegram
   - Отправьте команду `/start`
   - Следуйте инструкциям бота

2. **Генерация данных**
   - Используйте `/generate` для создания случайного пользователя
   - Настройте параметры через `/settings`

3. **Настройка параметров**
   - В меню настроек выберите нужные параметры
   - Все настройки сохраняются для каждого пользователя

## 🛠 Управление ботом

### Мониторинг
```bash
# Просмотр логов
tail -f logs/bot.log

# Проверка статуса
sudo systemctl status telegrambot
```

### Управление сервисом
```bash
# Остановка бота
sudo systemctl stop telegrambot

# Перезапуск бота
sudo systemctl restart telegrambot
```

### Обновление
```bash
# Останавливаем сервис
sudo systemctl stop telegrambot

# Обновляем код
git pull

# Обновляем зависимости
pip install -r requirements.txt

# Запускаем сервис
sudo systemctl start telegrambot
```

## ⚠️ Важные замечания

1. **Безопасность**
   - Храните токен бота в безопасном месте
   - Регулярно меняйте пароли
   - Используйте файрвол

2. **Бэкапы**
   - Регулярно делайте резервные копии базы данных
   - Храните копии конфигурационных файлов

3. **Обновления**
   - Регулярно обновляйте систему
   - Следите за обновлениями зависимостей

## 📄 Лицензия

MIT License

## 👥 Поддержка

При возникновении проблем создавайте issue в репозитории проекта или обращайтесь к администратору бота. 