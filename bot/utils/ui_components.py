"""UI компоненты для взаимодействия с ботом"""
import discord
from discord.ext import commands
from datetime import timedelta
import asyncio
from bot.utils.logger import log_action
from config import settings

class VerificationView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=None)
        self.target_member = target_member

    async def check_permissions(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(settings.ADMIN_ROLE_ID)
        owner_role = interaction.guild.get_role(settings.OWNER_ROLE_ID)
        if admin_role not in interaction.user.roles and owner_role not in interaction.user.roles:
            await interaction.response.send_message("🚫 У вас нет прав для верификации.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Участник 👤", style=discord.ButtonStyle.success, custom_id="verify_member")
    async def verify_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_permissions(interaction):
            await self.verify_user(interaction)

    async def verify_user(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(self.target_member.id)
        if not member:
            await interaction.response.edit_message(content=f"❌ Пользователь покинул сервер до верификации.", view=None)
            return  
        base_role = guild.get_role(settings.MEMBER_ROLE_ID)
        roles_to_add = []
        if base_role: 
            roles_to_add.append(base_role)    
        try:
            await member.add_roles(*roles_to_add)
            for child in self.children:
                child.disabled = True 
            await interaction.response.edit_message(
                content=f"✅ Участник {member.mention} успешно верифицирован модератором {interaction.user.mention}.", 
                view=self
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота не хватает прав!", ephemeral=True)

class SpamActionView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=None)
        self.target_member = target_member

    async def check_permissions(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(settings.ADMIN_ROLE_ID)
        owner_role = interaction.guild.get_role(settings.OWNER_ROLE_ID)
        if admin_role not in interaction.user.roles and owner_role not in interaction.user.roles:
            await interaction.response.send_message("🚫 У вас нет прав для этого.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Забанить 🔨", style=discord.ButtonStyle.danger, custom_id="spam_ban")
    async def ban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_permissions(interaction):
            guild = interaction.guild
            member = guild.get_member(self.target_member.id)
            if member:
                reason = "Спам (Решение администратора/владельца)"
                await member.ban(reason=reason)
                await asyncio.to_thread(log_action, "ban", member.id, interaction.user.id, reason)
                
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content=f"🔨 Участник {self.target_member.mention} был забанен за спам модератором {interaction.user.mention}.", view=self)
            else:
                await interaction.response.edit_message(content="❌ Пользователь уже покинул сервер.", view=None)

    @discord.ui.button(label="Снять таймаут 🕊️", style=discord.ButtonStyle.success, custom_id="spam_forgive")
    async def forgive_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_permissions(interaction):
            guild = interaction.guild
            member = guild.get_member(self.target_member.id)
            if member:
                reason = "Оправдан администратором/владельцем"
                await member.timeout(None, reason=reason)
                await asyncio.to_thread(log_action, "unmute", member.id, interaction.user.id, reason)
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content=f"🕊️ Таймаут с {self.target_member.mention} был снят модератором {interaction.user.mention}.", view=self)
            else:
                await interaction.response.edit_message(content="❌ Пользователь уже покинул сервер.", view=None)
