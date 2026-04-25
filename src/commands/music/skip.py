import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Accedemos al MusicManager centralizado en el bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="skip", 
        description="Salta la canción actual y pasa a la siguiente en la cola"
    )
    async def skip(self, interaction: discord.Interaction):
        """Maneja la petición de salto de pista en Sybaru."""
        
        # 1. Verificación básica: ¿Está el bot conectado?
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message(
                "❌ **Sybaru** no está conectado a ningún canal de voz.", 
                ephemeral=True
            )

        # 2. Seguridad: ¿Está el usuario en el mismo canal que el bot?
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "⚠️ Debes estar en el mismo canal de voz que **Sybaru** para saltar la música.", 
                ephemeral=True
            )

        # 3. Estado de reproducción: ¿Hay algo sonando o pausado?
        if not vc.is_playing() and not vc.is_paused():
            return await interaction.response.send_message(
                "⚠️ No hay ninguna canción activa para saltar ahora mismo.", 
                ephemeral=True
            )

        # 4. Ejecución del salto
        # Importante: vc.stop() disparará la siguiente canción si el player tiene un loop 'after'
        exito = self.manager.skip(interaction)

        if exito:
            embed = discord.Embed(
                description="⏭️ **Canción saltada correctamente.**",
                color=discord.Color.blue() 
            )
            
            # Enviamos la confirmación
            await interaction.response.send_message(embed=embed)
            
            # Borrado automático para mantener el canal limpio
            await asyncio.sleep(10)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            await interaction.response.send_message(
                "❌ No pude saltar la pista. Verifica si hay canciones en la cola.",
                ephemeral=True
            )

async def setup(bot):
    """Carga el Cog en Sybaru."""
    await bot.add_cog(Skip(bot))