import discord
from discord.ext import commands
from discord import app_commands

class Stop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="stop", 
        description="Detiene la música, vacía la cola y saca al bot del canal"
    )
    async def stop(self, interaction: discord.Interaction):
        """Detiene todo y desconecta al bot."""
        
        # 1. Verificar si el bot está en voz
        if not interaction.guild.voice_client:
            return await interaction.response.send_message(
                "❌ No estoy en ningún canal de voz.", 
                ephemeral=True
            )

        # 2. Limpieza de datos en el Manager (vacía cola y quita loop)
        self.manager.stop(interaction)

        # 3. DESCONEXIÓN: Esto hace que el bot se salga del canal
        await interaction.guild.voice_client.disconnect()

        # 4. Respuesta de despedida personalizada
        embed = discord.Embed(
            description="⏹️ **Música detenida, hasta pronto.**",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stop(bot))