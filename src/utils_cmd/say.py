import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Say(commands.Cog):
    """
    Cog que permite al bot repetir mensajes del usuario.
    Diseñado para ser discreto y funcional.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="Haz que Sybaru diga algo por ti (el comando será invisible)."
    )
    @app_commands.describe(mensaje="El texto que quieres que el bot transmita")
    @app_commands.checks.has_permissions(send_messages=True)
    async def say(self, interaction: discord.Interaction, mensaje: str):
        """
        Envía un mensaje en el canal actual a nombre del bot.
        Incluye un efecto de 'Escribiendo...' para mayor realismo.
        """
        
        # 1. Validación de seguridad básica
        if len(mensaje) > 2000:
            return await interaction.response.send_message(
                "❌ El mensaje es demasiado largo para Discord.", 
                ephemeral=True
            )

        # 2. Confirmación inmediata y silenciosa para el usuario
        # Usamos un mensaje efímero que se auto-elimina casi al instante
        await interaction.response.send_message("✅ Transmitiendo...", ephemeral=True, delete_after=0.1)

        # 3. Efecto de realismo
        # El bot activa el estado 'Escribiendo...' durante 1.5 segundos
        async with interaction.channel.typing():
            await asyncio.sleep(1.5)
            
            # 4. Envío del mensaje final
            await interaction.channel.send(mensaje)

    @say.error
    async def say_error(self, interaction: discord.Interaction, error):
        """Maneja errores de permisos para el comando say."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para enviar mensajes aquí.", 
                ephemeral=True
            )

async def setup(bot):
    """Carga del módulo de repetición Say."""
    await bot.add_cog(Say(bot))