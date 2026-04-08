import discord
from discord.ext import commands
from discord import app_commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="Haz que el bot diga algo por ti (el comando será invisible)"
    )
    @app_commands.describe(mensaje="¿Qué quieres que diga el bot?")
    async def say(self, interaction: discord.Interaction, mensaje: str):
        # 1. Enviamos una respuesta efímera para que Discord no marque el comando como "fallido"
        # Pero solo tú verás que el bot recibió la orden.
        await interaction.response.send_message("✅ Mensaje enviado", ephemeral=True, delete_after=0.1)

        # 2. El bot envía el mensaje en el canal actual
        await interaction.channel.send(mensaje)

async def setup(bot):
    await bot.add_cog(Say(bot))