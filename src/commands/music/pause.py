import discord
from discord.ext import commands
from discord import app_commands

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(name="pause", description="Pausa la canción que está sonando")
    async def pause(self, interaction: discord.Interaction):
        # 1. Verificar si hay un cliente de voz activo
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("❌ No hay música para pausar.", ephemeral=True)

        # 2. Intentar pausar desde el Manager
        exito = self.manager.pause(interaction)

        if exito:
            await interaction.response.send_message("⏸️ **Música pausada.** Usa `/resume` para continuar.")
        else:
            await interaction.response.send_message("⚠️ La música ya está pausada o no hay nada reproduciéndose.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Pause(bot))