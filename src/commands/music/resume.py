import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Vinculación con el MusicManager centralizado del bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="resume", 
        description="Reanuda la canción que estaba pausada"
    )
    async def resume(self, interaction: discord.Interaction):
        """Continúa la reproducción si el bot se encuentra en estado pausado."""
        
        # 1. Validación de conexión: ¿Está el bot en un canal?
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message(
                "❌ No hay ninguna sesión de música activa.", 
                ephemeral=True
            )

        # 2. Seguridad: ¿El usuario está en el mismo canal que el bot?
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "⚠️ Debes estar en el mismo canal de voz que yo para reanudar la música.", 
                ephemeral=True
            )

        # 3. Ejecución de la reanudación mediante el Manager
        exito = self.manager.resume(interaction)

        if exito:
            embed = discord.Embed(
                description="▶️ **Música reanudada.**",
                color=discord.Color.green() # Verde para indicar reproducción activa
            )
            await interaction.response.send_message(embed=embed)
            
            # Limpieza del mensaje tras 15 segundos para mantener el canal ordenado
            await asyncio.sleep(15)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            # Si no tuvo éxito es porque probablemente no estaba pausado
            await interaction.response.send_message(
                "⚠️ La música no está pausada o ya se está reproduciendo.", 
                ephemeral=True
            )

async def setup(bot):
    """Carga el Cog de Resume en el bot."""
    await bot.add_cog(Resume(bot))