import discord
from discord.ext import commands
from discord import app_commands
# Importamos las funciones exactas de nuestra base de datos unificada
from src.utils.database import set_guild_prefix, reset_guild_prefix

class SetPrefix(commands.Cog):
    """
    Módulo de gestión de prefijos dinámicos para Sybaru.
    Conectado a la base de datos centralizada.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="prefix",
        description="Configura el prefijo de los comandos de texto para este servidor."
    )
    @app_commands.describe(
        accion="Elige si quieres cambiar o restablecer el prefijo",
        nuevo_prefix="Escribe el nuevo símbolo (ej: $, ., >)"
    )
    @app_commands.choices(accion=[
        app_commands.Choice(name="Cambiar", value="change"),
        app_commands.Choice(name="Restablecer", value="reset")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def prefix(
        self, 
        interaction: discord.Interaction, 
        accion: app_commands.Choice[str], 
        nuevo_prefix: str = None
    ):
        guild_id = interaction.guild.id

        if accion.value == "change":
            # Validaciones
            if nuevo_prefix is None:
                return await interaction.response.send_message(
                    "❌ Debes especificar un nuevo prefijo si eliges 'Cambiar'.", ephemeral=True, delete_after=15
                )
            
            if len(nuevo_prefix) > 5:
                return await interaction.response.send_message(
                    "❌ El prefijo es demasiado largo (máximo 5 caracteres).", ephemeral=True, delete_after=15
                )

            # Usamos la función de database.py
            if set_guild_prefix(guild_id, nuevo_prefix):
                mensaje = f"✅ El prefijo ha sido cambiado a: `{nuevo_prefix}`"
                color = discord.Color.green()
            else:
                return await interaction.response.send_message("❌ Error al acceder a la base de datos.", ephemeral=True)
        
        else:  # Acción: Restablecer
            # Usamos la función de reset de database.py
            if reset_guild_prefix(guild_id):
                mensaje = "🔄 El prefijo ha sido restablecido al valor por defecto (`!`)."
                color = discord.Color.blue()
            else:
                return await interaction.response.send_message("❌ Error al restablecer el prefijo.", ephemeral=True)

        # Embed de confirmación
        embed = discord.Embed(
            title="⚙️ Configuración de Sybaru",
            description=f"> {mensaje}",
            color=color
        )
        embed.set_footer(text=f"Ajuste realizado por {interaction.user.display_name}")

        # Enviamos la confirmación (se borra en 15s para mantener limpio el canal)
        await interaction.response.send_message(embed=embed, delete_after=15)

    @prefix.error
    async def prefix_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden gestionar el prefijo del bot.", 
                ephemeral=True,
                delete_after=15
            )

async def setup(bot):
    await bot.add_cog(SetPrefix(bot))   