"""Функции для создания приветственных и прощальных баннеров"""
from PIL import Image, ImageDraw, ImageFont
import discord
import io
from config import settings

def get_welcome_text(member):
    """Текст приветствия для нового участника"""
    return (
        f"Добро пожаловать на сервер, {member.mention}!\n\n"
        f"Пожалуйста, обязательно ознакомься с нашими правилами в канале <#{settings.RULES_CHANNEL_ID}>."
    )

def get_goodbye_text(member):
    """Текст прощания для вышедшего участника"""
    return f"Участник {member.name} покинул сервер."

def _load_minecraft_font(size):
    """Загружает шрифт Minecraft с заданным размером"""
    try:
        return ImageFont.truetype("assets/minecraft.ttf", size)
    except IOError:
        print("⚠️ Не удалось загрузить шрифт minecraft.ttf, используется стандартный")
        return ImageFont.load_default()

def _draw_rectangle_avatar(bg, avatar_bytes, position, width, height):
    """Рисует прямоугольный аватар на фоне
    
    Args:
        bg: Фоновое изображение
        avatar_bytes: Байты аватара пользователя
        position: Кортеж (x, y) позиции вставки
        width: Ширина аватара
        height: Высота аватара
    """
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((width, height), Image.Resampling.LANCZOS)
    
    # Вставляем прямоугольный аватар на фон
    bg.paste(avatar, position, avatar)

def _fit_text_to_width(draw, text, font, max_width, min_size=20):
    """Подгоняет размер шрифта под максимальную ширину"""
    current_size = font.size
    
    while current_size > min_size:
        test_font = _load_minecraft_font(current_size)
        bbox = draw.textbbox((0, 0), text, font=test_font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            return test_font
        
        current_size -= 2
    
    return _load_minecraft_font(min_size)

async def create_welcome_image(member: discord.Member):
    """Создает изображение приветствия для нового участника
    
    Параметры шаблона join.png:
    - Размер: 1748x510 пикселей
    - Аватар: 304x303 на позиции (76, 96)
    - Текст: позиция (460, 285), размер 38-42px
    - Заголовок "ДОБРО ПОЖАЛОВАТЬ!" уже на картинке
    """
    try:
        # Загружаем фоновое изображение join.png (1748x510)
        bg = Image.open("assets/join.png").convert("RGBA")
        
        # Получаем аватар участника
        avatar_bytes = await member.display_avatar.replace(size=512, format='png').read()
        
        # Параметры аватара согласно шаблону
        avatar_width = 294   # Ширина аватара
        avatar_height = 304  # Высота аватара
        avatar_x = 80        # Координата X
        avatar_y = 96        # Координата Y
        
        # Рисуем квадратный аватар
        _draw_rectangle_avatar(bg, avatar_bytes, (avatar_x, avatar_y), avatar_width, avatar_height)
        
        # Создаем объект для рисования текста
        draw = ImageDraw.Draw(bg)
        
        # Загружаем шрифт Minecraft (начальный размер 42px)
        font_text = _load_minecraft_font(42)
        
        # Формируем текст с никнеймом
        nickname = member.display_name
        text = f"{nickname} зашёл на сервер."
        
        # Параметры текста согласно шаблону
        text_x = 460  # Координата X текста
        text_y = 285  # Координата Y текста
        
        # Максимальная ширина для текста (от позиции до конца с отступом)
        max_text_width = bg.width - text_x - 50
        
        # Подгоняем размер шрифта (38-42px), если никнейм длинный
        font_text = _fit_text_to_width(draw, text, font_text, max_text_width, min_size=38)
        
        # Рисуем текст белым цветом (#FFFFFF)
        draw.text((text_x, text_y), text, fill="#FFFFFF", font=font_text)
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        bg.convert("RGB").save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(fp=buffer, filename="welcome.png")
    except Exception as e:
        print(f"⚠️ Ошибка создания картинки приветствия: {e}")
        import traceback
        traceback.print_exc()
        return None

async def create_goodbye_image(member: discord.Member):
    """Создает изображение прощания для вышедшего участника
    
    Параметры шаблона quit.png:
    - Размер: 1748x510 пикселей
    - Аватар: 304x303 на позиции (76, 96)
    - Текст: позиция (460, 285), размер 38-42px
    - Заголовок "ДО СВИДАНИЯ!" уже на картинке
    """
    try:
        # Загружаем фоновое изображение quit.png (1748x510)
        bg = Image.open("assets/quit.png").convert("RGBA")
        
        # Получаем аватар участника
        avatar_bytes = await member.display_avatar.replace(size=512, format='png').read()
        
        # Параметры аватара согласно шаблону (те же, что для приветствия)
        avatar_width = 304   # Ширина аватара
        avatar_height = 303  # Высота аватара
        avatar_x = 76        # Координата X
        avatar_y = 96        # Координата Y
        
        # Рисуем квадратный аватар
        _draw_rectangle_avatar(bg, avatar_bytes, (avatar_x, avatar_y), avatar_width, avatar_height)
        
        # Создаем объект для рисования текста
        draw = ImageDraw.Draw(bg)
        
        # Загружаем шрифт Minecraft (начальный размер 42px)
        font_text = _load_minecraft_font(42)
        
        # Формируем текст с никнеймом
        nickname = member.display_name
        text = f"{nickname} вышел с сервера."
        
        # Параметры текста согласно шаблону
        text_x = 460  # Координата X текста
        text_y = 285  # Координата Y текста
        
        # Максимальная ширина для текста
        max_text_width = bg.width - text_x - 50
        
        # Подгоняем размер шрифта (38-42px), если никнейм длинный
        font_text = _fit_text_to_width(draw, text, font_text, max_text_width, min_size=38)
        
        # Рисуем текст белым цветом (#FFFFFF)
        draw.text((text_x, text_y), text, fill="#FFFFFF", font=font_text)
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        bg.convert("RGB").save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(fp=buffer, filename="goodbye.png")
    except Exception as e:
        print(f"⚠️ Ошибка создания картинки прощания: {e}")
        import traceback
        traceback.print_exc()
        return None
