import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Stop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Conexión al Manager centralizado de Sybaru
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
        
        vc = interaction.guild.voice_client
        
        # 1. Validación: ¿El bot está conectado?
        if not vc:
            return await interaction.response.send_message(
                "❌ **Sybaru** no está en ningún canal de voz ahora mismo.", 
                ephemeral=True
            )

        # 2. Seguridad: ¿El usuario está en el mismo canal que Sybaru?
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "⚠️ Debes estar en el mismo canal de voz que **Sybaru** para detener la música.", 
                ephemeral=True
            )

        try:
            # 3. Limpiar tareas de desconexión automática si existen
            if hasattr(self.manager, 'disconnect_tasks'):
                task = self.manager.disconnect_tasks.get(interaction.guild_id)
                if task:
                    task.cancel()
                    # Borramos la referencia de la tarea cancelada
                    del self.manager.disconnect_tasks[interaction.guild_id]

            # 4. Detener audio y limpiar la cola en el manager
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            
            # Llamamos al método stop del manager para resetear listas y loops
            self.manager.stop(interaction)
            
            # 5. Desconexión física
            await vc.disconnect()

            # 6. Respuesta visual elegante
            embed = discord.Embed(
                title="🏮 Sesión Finalizada",
                description="⏹️ **La música se ha detenido y la cola ha sido vaciada.**\n¡Gracias por usar **Sybaru**!",
                color=discord.Color.red() 
            )
            embed.set_footer(text="Sybaru Music System")
            
            await interaction.response.send_message(embed=embed)

            # 7. Limpieza del chat: El mensaje desaparece tras 20 segundos
            await asyncio.sleep(20)
            try:
                await interaction.delete_original_response()
            except:
                pass

        except Exception as e:
            print(f"❌ Error en stop.py: {e}")

async def setup(bot):
    """Carga el Cog en el sistema."""
    await bot.add_cog(Stop(bot))