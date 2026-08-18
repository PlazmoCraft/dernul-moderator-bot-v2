"""Общие пользовательские команды"""
from discord.ext import commands
from collections import defaultdict
from datetime import timedelta
import discord
import asyncio
import psutil
import platform
import socket
import time
from datetime import datetime
from bot.utils.logger import log_action
from config import settings
from config.badwords import FORBIDDEN_WORDS
from config.badnicks import FORBIDDEN_NICKS

# Система репортов
active_reports = defaultdict(set)

async def setup_general_commands(bot):
    @bot.hybrid_command(name="report", description="Подать коллективную жалобу на пользователя в голосовом канале")
    async def report_user(ctx, user: discord.Member, *, reason: str = "Мешает в голосовом канале"):
        if ctx.author == user:
            await ctx.send("❌ Нельзя подать жалобу на самого себя.", ephemeral=True)
            return
        if not user.voice or not user.voice.channel:
            await ctx.send("❌ Этот пользователь не находится в голосовом канале.", ephemeral=True)
            return
        voice_channel = user.voice.channel
        if not getattr(ctx.author, 'voice', None) or ctx.author.voice.channel != voice_channel:
            await ctx.send("❌ Вы должны находиться в том же голосовом канале, что и нарушитель, чтобы подать жалобу.", ephemeral=True)
            return 
        valid_members = [m for m in voice_channel.members if not m.bot and m != user]
        required_votes = len(valid_members)
        if required_votes == 0:
            await ctx.send("❌ В канале нет других пользователей для голосования.", ephemeral=True)
            return
        active_reports[user.id].add(ctx.author.id)
        current_votes = len(active_reports[user.id])
        if current_votes >= required_votes:
            active_reports.pop(user.id, None)
            try:
                timeout_duration = discord.utils.utcnow() + timedelta(days=7)
                full_reason = f"Коллективная жалоба в войсе: {reason}"
                await user.timeout(timeout_duration, reason=full_reason)
                await user.move_to(None) 
                await asyncio.to_thread(log_action, "mute", user.id, "Коллективный репорт", full_reason)
                await ctx.send(f"⚖️ Решение принято! {user.mention} получил таймаут на 7 дней и был отключен от канала. Собрано {current_votes}/{required_votes} голосов.")
            except discord.Forbidden:
                await ctx.send("🚫 У бота не хватает прав выдать таймаут этому пользователю. Убедитесь, что роль бота выше роли нарушителя.")
        else:
            await ctx.send(f"⚠️ Жалоба на {user.name} принята! Остальные участники голосового канала должны тоже написать команду.\nСобрано голосов: **{current_votes} / {required_votes}**.")

    @bot.hybrid_command(name="info", description="Получить информацию о себе или другом пользователе")
    async def info_command(ctx, user: discord.Member = None):
        user = user or ctx.author
        embed = discord.Embed(
            title=f"Информация о {user.display_name}",
            color=user.color
        )
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)    
        embed.add_field(name="ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="Глобальное имя", value=user.global_name or user.name, inline=True)
        embed.add_field(name="Бот?", value="🤖 Да" if user.bot else "👤 Нет", inline=True)
        created_time = f"<t:{int(user.created_at.timestamp())}:F>"
        joined_time = f"<t:{int(user.joined_at.timestamp())}:F>" if user.joined_at else "Неизвестно"
        embed.add_field(name="📅 Аккаунт создан", value=created_time, inline=False)
        embed.add_field(name="📥 Зашел на сервер", value=joined_time, inline=False)
        roles = [role.mention for role in reversed(user.roles) if role.name != "@everyone"]
        roles_text = " ".join(roles) if roles else "Нет ролей"
        if len(roles_text) > 1024:
            roles_text = roles_text[:1000] + "..."  
        embed.add_field(name=f"🎭 Роли [{len(roles)}]", value=roles_text, inline=False)
        await ctx.send(embed=embed, ephemeral=True)

    @bot.hybrid_command(name="status", description="Проверка работы бота и показателей сервера")
    async def status_command(ctx):
        if ctx.guild.id != settings.MAIN_SERVER_ID:
            await ctx.send("Бот не настроен для работы на этом сервере.", ephemeral=True)
            return
        admin_role = ctx.guild.get_role(settings.ADMIN_ROLE_ID)
        owner_role = ctx.guild.get_role(settings.OWNER_ROLE_ID)
        is_admin = False
        if hasattr(ctx.author, "roles"):
            if admin_role in ctx.author.roles or owner_role in ctx.author.roles:
                is_admin = True
        if is_admin:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_cores = psutil.cpu_count(logical=True)
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024 ** 3)
            ram_total_gb = ram.total / (1024 ** 3)
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            os_name = platform.system()
            os_release = platform.release()
            hostname = socket.gethostname()
            try:
                ip_address = socket.gethostbyname(hostname)
            except Exception:
                ip_address = "Неизвестно"
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_td = timedelta(seconds=int(uptime_seconds))
            embed = discord.Embed(
                title="🖥️ Статус сервера",
                color=0x2b2d31
            )
            embed.add_field(name="💻 Процессор", value=f"**{cpu_usage}%** ({cpu_cores} ядер)", inline=True)
            embed.add_field(name="🧠 Оперативная память", value=f"**{ram_used_gb:.1f} GB** / {ram_total_gb:.1f} GB ({ram.percent}%)", inline=True)
            embed.add_field(name="💾 Диск", value=f"**{disk_used_gb:.1f} GB** / {disk_total_gb:.1f} GB ({disk.percent}%)", inline=True)
            embed.add_field(name="🖥️ ОС", value=f"{os_name} {os_release}", inline=True)
            embed.add_field(name="🌐 Сеть", value=f"`{hostname}`\n( `{ip_address}` )", inline=True)
            embed.add_field(name="⏱️ Время работы", value=str(uptime_td), inline=True)
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            embed.set_footer(text=f"Последнее обновление • {current_time}")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            words_count = len(FORBIDDEN_WORDS)
            nicks_count = len(FORBIDDEN_NICKS)
            await ctx.send(
                f"В словаре запрещенных слов: **{words_count}** шт.\n"
                f"В словаре запрещенных ников: **{nicks_count}** шт.", 
                ephemeral=True
            )

    @bot.hybrid_command(name="help", description="Получить список всех команд бота")
    async def help_command(ctx):
        embed = discord.Embed(
            title="📜 Список команд",
            description="Здесь собраны все доступные команды.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="👤 Для всех",
            value=(
                "`/help` — Показать это сообщение.\n"
                "`/info [@пользователь]` — Информация о себе или другом участнике.\n"
                "`/status` — Проверка статуса бота.\n"
                "`/report @пользователь [причина]` — Запустить голосование против нарушителя в твоем голосовом канале."
            ),
            inline=False
        )
        is_owner = ctx.guild and ctx.author.id == ctx.guild.owner_id
        is_admin = False
        if hasattr(ctx.author, "guild_permissions"):
            is_admin = ctx.author.guild_permissions.administrator
        if is_owner or is_admin:
            embed.add_field(
                name="🛠️ Для администрации",
                value=(
                    "`/ban @пользователь/ID [причина]` — Забанить пользователя.\n"
                    "`/kick @пользователь/ID [причина]` — Выгнать пользователя (кик).\n"
                    "`/unban ID [причина]` — Разбанить пользователя по его ID.\n"
                    "`/mute @пользователь/ID [время] [причина]` — Выдать таймаут (Форматы: `60`, `5m`, `1h`, `7d`).\n"
                    "`/unmute @пользователь/ID [причина]` — Снять таймаут с пользователя.\n"
                    "`/clear [число] (или /clear user:@упоминание sum:[число])` — Удалить сообщения."
                ),
                inline=False
            )
        await ctx.send(embed=embed, ephemeral=True)
