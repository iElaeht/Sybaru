import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="pause", 
        description="Pausa la reproduccion actual"
    )
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        
        if not vc:
            msg = await interaction.response.send_message(
                "No hay una conexion activa a un canal de voz", 
                ephemeral=True
            )
            return

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            msg = await interaction.response.send_message(
                "Debes estar en el mismo canal de voz para pausar la musica", 
                ephemeral=True
            )
            return

        exito = self.manager.pause(interaction)

        if exito:
            embed = discord.Embed(
                description="Reproduccion pausada. Usa /resume para continuar",
                color=discord.Color.from_rgb(43, 45, 49)
            )
            await interaction.response.send_message(embed=embed)
            
            await asyncio.sleep(15)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            await interaction.response.send_message(
                "La musica ya esta pausada o no hay audio en reproduccion", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Pause(bot))