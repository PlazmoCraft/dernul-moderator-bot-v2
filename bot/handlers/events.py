"""Обработчики событий Discord"""
import discord
from datetime import timedelta
from collections import defaultdict
import asyncio
import string
import time
from config.badwords import FORBIDDEN_WORDS
from config import settings
from bot.utils.logger import log_action
from bot.utils.nickname_checker import is_bad_nick, handle_bad_nick
from bot.utils.welcome import get_welcome_text, get_goodbye_text, create_welcome_image, create_goodbye_image
from bot.utils.ui_components import VerificationView, SpamActionView
from openai import AsyncOpenAI

# Антиспам система
user_messages = defaultdict(list)
SPAM_LIMIT = 3
SPAM_TIME = 5

# Инициализация NVIDIA клиента
nvidia_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.NVIDIA_API_KEY
)

async def on_ready(bot):
    """Обработчик события готовности бота"""
    from bot.utils.logger import pb
    try:
        pb.admins.auth_with_password(settings.PB_ADMIN_EMAIL, settings.PB_ADMIN_PASSWORD)
        print("Успешно подключено к PocketBase.")
    except Exception as e:
        print(f"Ошибка подключения к PocketBase: {e}")  
    await bot.tree.sync()
    print(f'Бот {bot.user} запущен и готов к работе.')
    guild = bot.get_guild(settings.MAIN_SERVER_ID)
    if guild:
        print("Запуск проверки никнеймов текущих участников...")
        offenders_count = 0
        for member in guild.members:
            if not member.bot and await is_bad_nick(member):
                bot.loop.create_task(handle_bad_nick(member, bot.user.id))
                offenders_count += 1
                await asyncio.to_thread(
                    log_action, 
                    "bad_nick_detected", 
                    member.id, 
                    bot.user.id, 
                    f"Обнаружен запрещенный ник @{member.name}"
                )    
        print(f"Проверка никнеймов завершена. Найдено нарушителей: {offenders_count}")

async def on_message(message, bot):
    """Обработчик новых сообщений"""
    if message.author.bot:
        return
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    # Проверка локального фильтра
    text = message.content.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words_in_message = text.split()
    if any(badword.lower() in words_in_message for badword in FORBIDDEN_WORDS):
        try:
            await message.delete()
            warning = await message.channel.send(f"🚫 {message.author.mention}, использование таких слов на сервере запрещено!")
            await asyncio.to_thread(log_action, "delete_message_local", message.author.id, bot.user.id, "Использование запрещенного слова (Локальный фильтр)")
            await asyncio.sleep(5)
            await warning.delete()
        except discord.Forbidden:
            pass
        return

    # Проверка через NVIDIA AI
    if message.content:
        try:
            completion = await nvidia_client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-safety-guard-8b-v3",
                messages=[{"role": "user", "content": message.content}],
                stream=False
            )
            ai_response = completion.choices[0].message.content.lower()
            if "unsafe" in ai_response:
                try:
                    await message.delete()
                    warning = await message.channel.send(f"🚫 {message.author.mention}, нейросеть заблокировала ваше сообщение из-за нарушения правил безопасности!")
                    await asyncio.to_thread(log_action, "delete_message_ai", message.author.id, bot.user.id, "Заблокировано нейросетью NVIDIA")
                    await asyncio.sleep(5)
                    await warning.delete()
                except discord.Forbidden:
                    pass
                return
        except Exception as e:
            print(f"⚠️ Ошибка проверки через NVIDIA API: {e}")

    # Антиспам проверка
    user_id = message.author.id
    now = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < SPAM_TIME]
    user_messages[user_id].append(now)
    if len(user_messages[user_id]) >= SPAM_LIMIT:
        user_messages[user_id].clear()
        try:
            timeout_duration = discord.utils.utcnow() + timedelta(days=7)
            reason = "Спам в чате"
            await message.author.timeout(timeout_duration, reason=reason)
            await asyncio.to_thread(log_action, "mute", message.author.id, bot.user.id, reason)
            admin_channel = bot.get_channel(settings.ADMIN_CHANNEL_ID)
            if admin_channel:
                view = SpamActionView(target_member=message.author)
                await admin_channel.send(
                    f"<@&{settings.ADMIN_ROLE_ID}> <@&{settings.OWNER_ROLE_ID}> ⚠️ Участник {message.author.mention} спамит!\n"
                    f"Ему автоматически выдан **таймаут на 7 дней**. Что будем делать?", 
                    view=view
                )
        except discord.Forbidden:
            pass
    await bot.process_commands(message)

async def on_member_join(member, bot):
    """Обработчик присоединения нового участника"""
    if await is_bad_nick(member):
        bot.loop.create_task(handle_bad_nick(member, bot.user.id))
    
    channel = bot.get_channel(settings.CHANNEL_ID)
    if channel:
        welcome_image = await create_welcome_image(member)
        if welcome_image:
            await channel.send(content=get_welcome_text(member), file=welcome_image)
        else:
            await channel.send(get_welcome_text(member))
    
    admin_channel = bot.get_channel(settings.ADMIN_CHANNEL_ID)
    if admin_channel:
        view = VerificationView(target_member=member)
        await admin_channel.send(
            f"<@&{settings.ADMIN_ROLE_ID}> <@&{settings.OWNER_ROLE_ID}>, новый участник {member.mention} ({member.name}) ожидает верификации.",
            view=view
        )

async def on_member_update(before, after, bot):
    """Обработчик обновления участника"""
    if before.display_name != after.display_name or before.name != after.name:
        if await is_bad_nick(after):
            bot.loop.create_task(handle_bad_nick(after, bot.user.id))

async def on_user_update(before, after, bot):
    """Обработчик обновления пользователя"""
    if before.global_name != after.global_name or before.name != after.name:
        guild = bot.get_guild(settings.MAIN_SERVER_ID)
        if guild:
            member = guild.get_member(after.id)
            if member and await is_bad_nick(member):
                bot.loop.create_task(handle_bad_nick(member, bot.user.id))

async def on_member_remove(member, bot):
    """Обработчик выхода участника"""
    channel = bot.get_channel(settings.LEAVE_CHANNEL_ID)
    if channel:
        goodbye_image = await create_goodbye_image(member)
        if goodbye_image:
            await channel.send(content=get_goodbye_text(member), file=goodbye_image)
        else:
            await channel.send(get_goodbye_text(member))
