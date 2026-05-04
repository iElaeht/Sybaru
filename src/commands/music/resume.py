import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="resume", 
        description="Reanuda la cancion que estaba pausada"
    )
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)

        if not vc:
            msg = await interaction.response.send_message(
                "No hay una sesion de musica activa", 
                ephemeral=True
            )
            return

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            msg = await interaction.response.send_message(
                "Debes estar en el mismo canal de voz para reanudar la musica", 
                ephemeral=True
            )
            return

        exito = self.manager.resume(interaction)

        if exito:
            embed = discord.Embed(
                description="Musica reanudada",
                color=COLOR_SYBARU
            )
            await interaction.response.send_message(embed=embed)
            
            await asyncio.sleep(15)
            try:
                await interaction.delete_original_response()
            except:
                pass
        else:
            await interaction.response.send_message(
                "La musica no esta pausada o ya se esta reproduciendo", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Resume(bot))