import discord
import asyncio
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
        description="Detiene la musica, vacia la cola y desconecta al bot"
    )
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)
        
        if not vc:
            return await interaction.response.send_message(
                "El bot no esta en un canal de voz", 
                ephemeral=True
            )

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "Debes estar en el mismo canal de voz para detener la musica", 
                ephemeral=True
            )

        try:
            if hasattr(self.manager, 'disconnect_tasks'):
                task = self.manager.disconnect_tasks.get(interaction.guild_id)
                if task:
                    task.cancel()
                    del self.manager.disconnect_tasks[interaction.guild_id]

            if vc.is_playing() or vc.is_paused():
                vc.stop()
            
            self.manager.stop(interaction)
            await vc.disconnect()

            embed = discord.Embed(
                title="Sesion Finalizada",
                description="La musica se ha detenido y la cola ha sido vaciada",
                color=COLOR_SYBARU
            )
            
            await interaction.response.send_message(embed=embed)

            await asyncio.sleep(20)
            try:
                await interaction.delete_original_response()
            except:
                pass

        except Exception as e:
            print(f"Error en Stop: {e}")

async def setup(bot):
    await bot.add_cog(Stop(bot))