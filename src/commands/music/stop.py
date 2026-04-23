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
        description="Detiene la música, vacía la cola y desconecta a Sybaru del canal"
    )
    async def stop(self, interaction: discord.Interaction):
        """Detiene la reproducción actual y saca al bot del canal de voz."""
        
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            return await interaction.response.send_message(
                "❌ **Sybaru** no está en ningún canal de voz ahora mismo.", 
                ephemeral=True
            )

        try:
            # 1. Cancelar cualquier temporizador de desconexión activa (si existe)
            if hasattr(self.manager, 'disconnect_tasks'):
                task = self.manager.disconnect_tasks.get(interaction.guild_id)
                if task:
                    task.cancel()

            # 2. Detener audio y limpiar manager
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()
            
            self.manager.stop(interaction)
        except Exception as e:
            print(f"Error al limpiar música en stop: {e}")

        # 3. Desconexión física
        await voice_client.disconnect()

        # 4. Respuesta visual
        embed = discord.Embed(
            title="🏮 Sesión Finalizada",
            description="⏹️ **La música se ha detenido y me he retirado del canal.**\n¡Espero verte pronto!",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_footer(text="Sybaru Music System")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stop(bot))