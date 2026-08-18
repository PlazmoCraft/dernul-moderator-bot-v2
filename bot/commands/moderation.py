"""Обработчики команд модерации"""
from discord.ext import commands
from datetime import timedelta
import discord
import asyncio
from bot.utils.logger import log_action
from config import settings

async def setup_moderation_commands(bot):
    @bot.hybrid_command(name="kick", description="Выгнать (кикнуть) пользователя с сервера")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def kick_user(ctx, user: str, *, reason: str = "Нарушение правил сервера"):
        try:
            member = await commands.MemberConverter().convert(ctx, user)
            await member.kick(reason=reason)
            await asyncio.to_thread(log_action, "kick", member.id, ctx.author.id, reason)
            await ctx.send(f"👢 Участник {member.mention} был изгнан с сервера. Причина: {reason}")
        except commands.MemberNotFound:
            await ctx.send("❌ Пользователь не найден на сервере. Укажите правильное `@упоминание` или `ID`.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("🚫 У бота не хватает прав для кика (возможно, вы пытаетесь кикнуть администратора, или роль бота ниже роли пользователя).", ephemeral=True)
        except discord.HTTPException:
            await ctx.send("⚠️ Ошибка запроса. Попробуйте позже.", ephemeral=True)

    @bot.hybrid_command(name="ban", description="Забанить пользователя (по упоминанию или ID)")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def smart_ban(ctx, user: str, *, reason: str = "Нарушение правил сервера"):
        try:
            user = await commands.UserConverter().convert(ctx, user)
            await ctx.guild.ban(user, reason=reason)
            await asyncio.to_thread(log_action, "ban", user.id, ctx.author.id, reason)
            await ctx.send(f"🔨 {user.mention} был забанен. Причина: {reason}")
        except commands.UserNotFound:
            try:
                user_id = int(user.strip('<@!>'))
                user_obj = discord.Object(id=user_id)
                await ctx.guild.ban(user_obj, reason=reason)
                await asyncio.to_thread(log_action, "ban", user_id, ctx.author.id, reason)
                await ctx.send(f"🔨 Пользователь с ID `{user_id}` был превентивно заблокирован. Причина: {reason}")
            except ValueError:
                await ctx.send("❌ Укажите правильное `@упоминание` или `ID` (только цифры).", ephemeral=True)
            except discord.NotFound:
                await ctx.send("❌ Пользователь с таким ID не найден в базе Discord.", ephemeral=True)
            except discord.Forbidden:
                await ctx.send("🚫 У бота не хватает прав для блокировки (возможно, вы пытаетесь забанить администратора).", ephemeral=True)
            except discord.HTTPException:
                await ctx.send("⚠️ Ошибка запроса. Проверьте правильность ID.", ephemeral=True)

    @bot.hybrid_command(name="unban", description="Разбанить пользователя по ID")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def unban_user(ctx, user: str, *, reason: str = "Решение администратора"):
        try:
            target_id = int(user.strip('<@!>'))
            user_obj = discord.Object(id=target_id)
            await ctx.guild.unban(user_obj, reason=reason)
            await asyncio.to_thread(log_action, "unban", target_id, ctx.author.id, reason)
            await ctx.send(f"🕊️ Пользователь с ID `{target_id}` был разбанен. Причина: {reason}")
        except ValueError:
             await ctx.send("❌ Укажите правильный `ID` пользователя (только цифры).", ephemeral=True)
        except discord.NotFound:
            await ctx.send("❌ Пользователь с таким ID не находится в списке забаненных.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("🚫 У бота не хватает прав для разблокировки.", ephemeral=True)
        except discord.HTTPException:
            await ctx.send("⚠️ Произошла ошибка при попытке разбана. Проверьте правильность ID.", ephemeral=True)

    @bot.hybrid_command(name="mute", description="Выдать мут пользователю (Например: 10m, 1h, 1d)")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def mute_user(ctx, user: str, time: str = "60", *, reason: str = "Нарушение правил сервера"):
        try:
            duration_lower = time.lower()
            seconds = 0
            if duration_lower.endswith('m'):
                seconds = int(duration_lower[:-1]) * 60
            elif duration_lower.endswith('h'):
                seconds = int(duration_lower[:-1]) * 3600
            elif duration_lower.endswith('d'):
                seconds = int(duration_lower[:-1]) * 86400
            elif duration_lower.isdigit():
                seconds = int(duration_lower)
            else:
                await ctx.send("⚠️ Ошибка времени. Форматы: `60` (сек), `5m` (мин), `1h` (час), `7d` (дни).", ephemeral=True)
                return
            member = await commands.MemberConverter().convert(ctx, user)
            timeout_duration = discord.utils.utcnow() + timedelta(seconds=seconds)
            await member.timeout(timeout_duration, reason=reason)
            await asyncio.to_thread(log_action, "mute", member.id, ctx.author.id, f"{reason} ({time})")
            await ctx.send(f"🔇 Участник {member.mention} получил таймаут на **{time}**. Причина: {reason}")
        except ValueError:
             await ctx.send("⚠️ Неправильный формат времени. Убедитесь, что используете цифры (например, `10m`).", ephemeral=True)
        except commands.MemberNotFound:
            await ctx.send("❌ Пользователь не найден на сервере. Нельзя выдать мут тому, кого здесь нет.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("🚫 У бота не хватает прав выдать таймаут этому участнику (возможно, его роль выше роли бота).", ephemeral=True)

    @bot.hybrid_command(name="unmute", description="Снять таймаут (мут) с пользователя")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def unmute_user(ctx, user: str, *, reason: str = "Решение администратора"):
        try:
            member = await commands.MemberConverter().convert(ctx, user)
            await member.timeout(None, reason=reason)
            await asyncio.to_thread(log_action, "unmute", member.id, ctx.author.id, reason)
            await ctx.send(f"🔊 Таймаут с участника {member.mention} был снят. Причина: {reason}")
        except commands.MemberNotFound:
            await ctx.send("❌ Пользователь не найден на сервере. Возможно, он уже покинул сервер или указан неверно.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("🚫 У бота не хватает прав снять таймаут с этого участнику.", ephemeral=True)

    @bot.hybrid_command(name="clear", description="Удалить сообщения: можно указать пользователя и количество")
    @commands.has_any_role(settings.ADMIN_ROLE_ID, settings.OWNER_ROLE_ID)
    async def smart_clear(ctx, user: discord.User = None, sum: int = 5):
        if ctx.interaction is None:
            try:
                await ctx.message.delete()
            except discord.NotFound:
                pass      
        try:
            if user is None:
                deleted = await ctx.channel.purge(limit=sum)
                msg = await ctx.send(f"🧹 Удалено {len(deleted)} сообщений.")
            else:
                def is_user(msg_obj):
                    return msg_obj.author.id == user.id
                deleted = await ctx.channel.purge(limit=sum, check=is_user)
                msg = await ctx.send(f"🧹 Удалено {len(deleted)} сообщений от пользователя {user.mention}.")
            await asyncio.sleep(4)
            try:
                await msg.delete()
            except discord.NotFound:
                pass
        except discord.Forbidden:
            await ctx.send("🚫 У бота не хватает прав для удаления сообщений в этом канале.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"⚠️ Ошибка при удалении: {e}", ephemeral=True)

    @smart_clear.error
    @smart_ban.error
    @kick_user.error
    @unban_user.error
    @mute_user.error
    @unmute_user.error
    async def admin_commands_error(ctx, error):
        if isinstance(error, (commands.MissingPermissions, commands.MissingAnyRole)):
            await ctx.send("🚫 У тебя нет прав для выполнения этой команды. Доступно только Администраторам и Владельцам.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Ты забыл указать цель, количество или время. Проверь команду.", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Ошибка формата. Убедись, что используешь правильные данные.", ephemeral=True)
