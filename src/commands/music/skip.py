import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="skip", 
        description="Salta la cancion actual y pasa a la siguiente en la cola"
    )
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)

        if not vc:
            return await interaction.response.send_message(
                "No hay una conexion activa a un canal de voz", 
                ephemeral=True
            )

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "Debes estar en el mismo canal de voz para usar este comando", 
                ephemeral=True
            )

        if not vc.is_playing() and not vc.is_paused():
            return await interaction.response.send_message(
                "No hay ninguna cancion activa para saltar ahora mismo", 
                ephemeral=True
            )

        exito = self.manager.skip(interaction)

        if exito:
            embed = discord.Embed(
                description="Cancion saltada correctamente",
                color=COLOR_SYBARU
            )
            
            await interaction.response.send_message(embed=embed)
            
            await asyncio.sleep(10)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            await interaction.response.send_message(
                "No se pudo saltar la pista",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Skip(bot))