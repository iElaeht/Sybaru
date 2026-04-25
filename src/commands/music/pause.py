import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Conexión al Manager centralizado
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="pause", 
        description="Pausa la reproducción actual"
    )
    async def pause(self, interaction: discord.Interaction):
        """Detiene temporalmente el flujo de audio."""
        
        # 1. Validación: ¿El bot está conectado?
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message(
                "❌ No estoy conectado a ningún canal de voz.", 
                ephemeral=True
            )

        # 2. Seguridad: ¿Usuario y bot están en el mismo canal?
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "⚠️ Debes estar en el mismo canal de voz que yo para pausar la música.", 
                ephemeral=True
            )

        # 3. Ejecutar pausa a través del Manager
        exito = self.manager.pause(interaction)

        if exito:
            embed = discord.Embed(
                description="⏸️ **Música pausada.** Usa `/resume` para continuar.",
                color=discord.Color.orange() # Naranja para indicar "espera"
            )
            await interaction.response.send_message(embed=embed)
            
            # Limpieza automática tras 15 segundos
            await asyncio.sleep(15)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            await interaction.response.send_message(
                "⚠️ La música ya está pausada o no hay nada sonando.", 
                ephemeral=True
            )

async def setup(bot):
    """Carga el Cog de Pausa."""
    await bot.add_cog(Pause(bot))