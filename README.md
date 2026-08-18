# Discord Dernul Moderator Bot v2

> **Это форк оригинального проекта**  
> Оригинальный репозиторий: [PlazmoCraft/dernul-moderator-bot](https://github.com/PlazmoCraft/dernul-moderator-bot)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Discord](https://img.shields.io/badge/Discord.py-Enabled-5865F2?style=for-the-badge&logo=discord)
![PocketBase](https://img.shields.io/badge/PocketBase-Database-B8E986?style=for-the-badge)
![NVIDIA AI](https://img.shields.io/badge/NVIDIA-AI_Safety-76B900?style=for-the-badge&logo=nvidia)

Продвинутый бот-модератор для Discord с автоматической модерацией, проверкой никнеймов и интеграцией с NVIDIA AI.

Этот многофункциональный Discord-бот предназначен для автоматической модерации, управления пользователями и защиты сервера. Бот автоматически проверяет сообщения с помощью ИИ, блокирует запрещенные слова и никнеймы, создает красивые приветственные изображения для новых участников и логирует все действия в базу данных PocketBase.

## 📁 Структура проекта

```
dernul-moderator-bot-main/
├── assets/                      # Ресурсы (картинки, шрифты)
│   ├── join.png                # Баннер приветствия
│   ├── quit.png                # Баннер прощания
│   ├── minecraft.ttf           # Шрифт Minecraft
│   ├── 44830476.png            # Старый баннер (можно удалить)
│   └── vcr-osd-mono-rusvhs-icons.ttf
├── bot/                         # Основной код бота
│   ├── commands/                # Команды бота
│   │   ├── __init__.py
│   │   ├── general.py          # Общие команды (info, help, status, report)
│   │   └── moderation.py       # Команды модерации (ban, kick, mute, etc.)
│   ├── handlers/                # Обработчики событий
│   │   ├── __init__.py
│   │   └── events.py           # События Discord (on_message, on_member_join, etc.)
│   ├── utils/                   # Утилиты
│   │   ├── __init__.py
│   │   ├── logger.py           # Логирование в PocketBase
│   │   ├── nickname_checker.py # Проверка запрещенных никнеймов
│   │   ├── ui_components.py    # UI компоненты (кнопки, формы)
│   │   └── welcome.py          # Генерация приветственных сообщений
│   └── __init__.py
├── config/                      # Конфигурация
│   ├── __init__.py
│   ├── settings.py             # Основные настройки
│   ├── badwords.py             # Список запрещенных слов
│   └── badnicks.py             # Список запрещенных никнеймов
├── main.py                      # Точка входа
└── README.md

```

## 🚀 Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd dernul-moderator-bot-main
   ```

2. **Установите зависимости:**
   ```bash
   pip install discord.py pillow pocketbase openai psutil
   ```

3. **Настройте конфигурацию:**
   Откройте `config/settings.py` и заполните следующие поля:
   ```python
   TOKEN = "ваш_discord_токен"
   NVIDIA_API_KEY = "ваш_nvidia_api_ключ"
   
   # ID каналов
   CHANNEL_ID = id_канала_приветствия
   LEAVE_CHANNEL_ID = id_канала_выхода
   RULES_CHANNEL_ID = id_канала_правил
   MAIN_SERVER_ID = id_сервера
   ADMIN_CHANNEL_ID = id_канала_админов
   
   # ID ролей
   OWNER_ROLE_ID = id_роли_владельца
   ADMIN_ROLE_ID = id_роли_админа
   MEMBER_ROLE_ID = id_роли_участника
   
   # PocketBase
   PB_URL = "url_вашей_pocketbase"
   PB_ADMIN_EMAIL = "admin@example.com"
   PB_ADMIN_PASSWORD = "пароль"
   ```

4. **Запустите бота:**
   ```bash
   python main.py
   ```

## 🛠️ Функции

### Приветствие и прощание
- ✅ Красивый баннер приветствия (`join.png`) с круглым аватаром
- ✅ Баннер прощания (`quit.png`) при выходе участника
- ✅ Кастомный шрифт Minecraft для текста
- ✅ Автоматическое масштабирование длинных никнеймов
- ✅ Текст с обводкой для читаемости на любом фоне

### Автоматическая модерация
- ✅ Фильтр запрещенных слов (локальный словарь)
- ✅ AI-модерация через NVIDIA Nemotron Safety Guard
- ✅ Антиспам система
- ✅ Проверка запрещенных никнеймов
- ✅ Автоматический таймаут за спам (7 дней)

### Команды модерации (только для админов)
- `/ban @пользователь [причина]` - Забанить пользователя
- `/kick @пользователь [причина]` - Кикнуть пользователя
- `/unban ID [причина]` - Разбанить по ID
- `/mute @пользователь [время] [причина]` - Выдать таймаут
- `/unmute @пользователь [причина]` - Снять таймаут
- `/clear [количество]` - Удалить сообщения

### Общие команды
- `/help` - Список всех команд
- `/info [@пользователь]` - Информация о пользователе
- `/status` - Статус бота и сервера
- `/report @пользователь [причина]` - Коллективная жалоба в войсе

### Система верификации
- Новые участники автоматически требуют верификации
- Админы получают уведомление с кнопкой верификации
- После верификации участник получает базовую роль

### Система проверки никнеймов
- Автоматическая проверка при входе
- Проверка при смене ника
- Предупреждение + 30 минут на смену
- Автоматический кик при повторном нарушении

## 📝 Логирование

Все действия модерации логируются в PocketBase:
- Баны/кики
- Муты/размуты
- Удаление сообщений
- Обнаружение запрещенных ников

## 🔧 Технологии

- **Discord.py** - Discord API
- **NVIDIA AI** - AI-модерация контента
- **PocketBase** - База данных для логов
- **Pillow** - Генерация приветственных изображений
- **psutil** - Мониторинг системы

## 📄 Лицензия

Этот проект распространяется под [MIT лицензией](https://raw.githubusercontent.com/PlazmoCraft/dernul-moderator-bot/refs/heads/main/LICENSE).

## 🙏 Авторство

Оригинальный автор: [PlazmoCraft](https://github.com/PlazmoCraft)  
Оригинальный репозиторий: [dernul-moderator-bot](https://github.com/PlazmoCraft/dernul-moderator-bot)

## 🤝 Вклад

### Настройка баннеров приветствия/прощания

Баннеры используют изображения `assets/join.png` и `assets/quit.png` со шрифтом Minecraft.

**Важно:** Координаты текста и аватара настроены примерно и требуют корректировки под ваши шаблоны!

📋 **Подробная инструкция:** См. файл `КООРДИНАТЫ_БАННЕРОВ.md`

#### Быстрая настройка координат:

Откройте `bot/utils/welcome.py` и измените:

```python
# В функциях create_welcome_image() и create_goodbye_image()

# Размер и позиция аватара
avatar_size = 200  # Диаметр круглого аватара
avatar_x = 100     # Отступ слева
avatar_y = (bg.height - avatar_size) // 2  # Вертикальная позиция

# Позиция заголовка ("ДОБРО ПОЖАЛОВАТЬ!" / "ДО СВИДАНИЯ!")
title_x = avatar_x + avatar_size + 100  # Горизонтально
title_y = bg.height // 2 - 100          # Вертикально

# Позиция подзаголовка (никнейм участника)
subtitle_y = title_y + 80  # Под заголовком

# Размеры шрифтов
font_title = _load_minecraft_font(60)     # Заголовок
font_subtitle = _load_minecraft_font(40)  # Подзаголовок
```

### Добавление новых картинок

При добавлении новых картинок:
1. Размещайте их в папке `assets/`
2. Обновляйте пути в `bot/utils/welcome.py`

## ⚙️ Дополнительная настройка

### Добавление запрещенных слов
Редактируйте `config/badwords.py` - добавьте слова в список `FORBIDDEN_WORDS`

### Добавление запрещенных никнеймов
Редактируйте `config/badnicks.py` - добавьте ники в список `FORBIDDEN_NICKS`

### Настройка антиспама
В `bot/handlers/events.py` измените:
```python
SPAM_LIMIT = 3  # Количество сообщений
SPAM_TIME = 5   # За сколько секунд
```

## 📞 Поддержка

Если возникли проблемы, проверьте:
1. Правильность токенов и ID в `config/settings.py`
2. Права бота на сервере (должны быть выше ролей пользователей)
3. Наличие всех зависимостей
4. Доступность PocketBase и NVIDIA API
