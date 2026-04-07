import discord
from discord.ext import commands
from discord import app_commands

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Conexión al Manager centralizado para compartir el estado del loop
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="loop", 
        description="Activa o desactiva la repetición de la canción actual"
    )
    async def loop(self, interaction: discord.Interaction):
        """Controlador para el estado de bucle (Loop)."""
        
        # 1. Validación: ¿El bot está en un canal de voz?
        if not interaction.guild.voice_client:
            return await interaction.response.send_message(
                "❌ No hay música reproduciéndose para activar el bucle.", 
                ephemeral=True
            )

        # 2. Llamamos al Manager para que cambie el interruptor (True -> False / False -> True)
        guild_id = interaction.guild_id
        nuevo_estado = self.manager.toggle_loop(guild_id)

        # 3. Respuesta visual atractiva
        if nuevo_estado:
            embed = discord.Embed(
                title="🔁 Bucle Activado",
                description="La canción actual se repetirá hasta que desactives el loop o la saltes.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Usa /loop de nuevo para desactivar.")
        else:
            embed = discord.Embed(
                title="➡️ Bucle Desactivado",
                description="La reproducción continuará con la siguiente canción en la cola.",
                color=discord.Color.light_grey()
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Loop(bot))