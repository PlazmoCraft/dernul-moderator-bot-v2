"""Проверка и обработка запрещенных никнеймов"""
import discord
import asyncio
from config.badnicks import FORBIDDEN_NICKS
from .logger import log_action

bad_nick_offenders = set()
active_nick_warnings = set()

async def is_bad_nick(member: discord.Member) -> bool:
    """Проверяет, содержит ли никнейм запрещенные слова"""
    names_to_check = [
        (member.name or "").lower(),
        (member.display_name or "").lower(),
        (member.global_name or "").lower()
    ]
    for bad_nick in FORBIDDEN_NICKS:
        bad_nick_lower = bad_nick.lower()
        for name in names_to_check:
            if bad_nick_lower in name:
                print(f"⚠️ Фильтр ников: Пользователь {name} попался на слове '{bad_nick_lower}'")
                return True               
    return False

async def handle_bad_nick(member: discord.Member, bot_user_id: int):
    """Логика предупреждения и кика за запрещенный никнейм."""
    if member.id in active_nick_warnings:
        return
    if member.id in bad_nick_offenders:
        try:
            await member.send("🚫 Вы снова зашли с запрещенным никнеймом или установили его. Вы немедленно изгнаны с сервера.")
        except discord.Forbidden:
            pass
        try:
            await member.kick(reason="Повторное использование запрещенного ника")
            await asyncio.to_thread(log_action, "kick", member.id, bot_user_id, "Мгновенный кик: повторный запрещенный ник")
        except discord.Forbidden:
            pass
        return
    active_nick_warnings.add(member.id)
    try:
        await member.send("⚠️ У вас обнаружен запрещенный никнейм! У вас есть **30 минут** на его смену. Если ник не будет изменен, вы будете автоматически кикнуты с сервера.")
    except discord.Forbidden:
        pass
    await asyncio.sleep(30 * 60)
    guild = member.guild
    current_member = guild.get_member(member.id)
    if current_member and await is_bad_nick(current_member):
        try:
            await current_member.send("⏳ Время вышло! Вы не сменили запрещенный никнейм и были изгнаны с сервера.")
        except discord.Forbidden:
            pass
        try:
            await current_member.kick(reason="Не сменил запрещенный ник за 30 минут")
            await asyncio.to_thread(log_action, "kick", current_member.id, bot_user_id, "Кик: не сменил запрещенный ник за 30 мин")
            bad_nick_offenders.add(current_member.id)
        except discord.Forbidden:
            pass
    active_nick_warnings.discard(member.id)
