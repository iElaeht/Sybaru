import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="loop", 
        description="Activa o desactiva la repeticion de la cancion actual"
    )
    async def loop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)

        if not vc:
            msg = await interaction.response.send_message(
                "No hay una conexion activa a un canal de voz", 
                ephemeral=True
            )
            return

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            msg = await interaction.response.send_message(
                "Debes estar en el mismo canal de voz para usar este comando", 
                ephemeral=True
            )
            return

        try:
            guild_id = interaction.guild_id
            nuevo_estado = self.manager.toggle_loop(guild_id)

            if nuevo_estado:
                embed = discord.Embed(
                    title="Bucle Activado",
                    description="La cancion actual se repetira indefinidamente",
                    color=COLOR_SYBARU
                )
            else:
                embed = discord.Embed(
                    title="Bucle Desactivado",
                    description="La reproduccion seguira el orden de la cola",
                    color=COLOR_SYBARU
                )
            
            await interaction.response.send_message(embed=embed)

            await asyncio.sleep(10)
            try:
                await interaction.delete_original_response()
            except:
                pass

        except Exception as e:
            print(f"Error en Loop: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Error al cambiar el estado del bucle", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Loop(bot))