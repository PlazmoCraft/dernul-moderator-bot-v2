"""Главный файл запуска Discord бота-модератора"""
import discord
from discord.ext import commands, tasks
import asyncio

from config import settings
from bot.handlers import events
from bot.commands.moderation import setup_moderation_commands
from bot.commands.general import setup_general_commands
from bot.utils.nickname_checker import is_bad_nick, handle_bad_nick

# Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Инициализация бота
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@tasks.loop(minutes=20)
async def check_bad_nicks_task():
    """Периодическая проверка никнеймов на сервере"""
    guild = bot.get_guild(settings.MAIN_SERVER_ID)
    if guild:
        for member in guild.members:
            if not member.bot and await is_bad_nick(member):
                bot.loop.create_task(handle_bad_nick(member, bot.user.id))

@bot.event
async def on_ready():
    """Событие запуска бота"""
    await events.on_ready(bot)
    check_bad_nicks_task.start()

@bot.event
async def on_message(message):
    """Событие получения сообщения"""
    await events.on_message(message, bot)

@bot.event
async def on_member_join(member):
    """Событие присоединения участника"""
    await events.on_member_join(member, bot)

@bot.event
async def on_member_update(before, after):
    """Событие обновления участника"""
    await events.on_member_update(before, after, bot)

@bot.event
async def on_user_update(before, after):
    """Событие обновления пользователя"""
    await events.on_user_update(before, after, bot)

@bot.event
async def on_member_remove(member):
    """Событие выхода участника"""
    await events.on_member_remove(member, bot)

async def setup_bot():
    """Настройка команд бота"""
    await setup_moderation_commands(bot)
    await setup_general_commands(bot)

async def main():
    """Основная функция запуска"""
    async with bot:
        await setup_bot()
        await bot.start(settings.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
