import discord
from discord.ext import commands
from discord import app_commands

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Conectamos al manager que ya vive en el bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="skip", 
        description="Salta la canción actual y reproduce la siguiente en la cola"
    )
    async def skip(self, interaction: discord.Interaction):
        """Controlador para saltar pistas."""
        
        # 1. Verificar si el bot está en un canal de voz
        if not interaction.guild.voice_client:
            return await interaction.response.send_message(
                "❌ No hay nada sonando que pueda saltar.", 
                ephemeral=True
            )

        # 2. Verificar si hay algo reproduciéndose
        if not interaction.guild.voice_client.is_playing():
            return await interaction.response.send_message(
                "⚠️ No hay ninguna canción en reproducción ahora mismo.", 
                ephemeral=True
            )

        # 3. Ejecutar el salto desde el Manager
        # El método .stop() de discord.py activa automáticamente el 'after' del play_next
        exito = self.manager.skip(interaction)

        if exito:
            embed = discord.Embed(
                description="⏭️ **Has saltado la canción actual.**",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ No se pudo saltar la canción.")

async def setup(bot):
    await bot.add_cog(Skip(bot))