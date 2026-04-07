import discord
from discord.ext import commands
from discord import app_commands

class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(name="resume", description="Reanuda la música pausada")
    async def resume(self, interaction: discord.Interaction):
        # 1. Verificar si hay un cliente de voz
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("❌ No hay ninguna sesión de música activa.", ephemeral=True)

        # 2. Intentar reanudar desde el Manager
        exito = self.manager.resume(interaction)

        if exito:
            await interaction.response.send_message("▶️ **Música reanudada.**")
        else:
            await interaction.response.send_message("⚠️ La música no está pausada.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Resume(bot))