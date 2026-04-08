import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class SetPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="prefix",
        description="Configura el prefijo de los comandos de texto para este servidor"
    )
    @app_commands.describe(
        accion="Elige si quieres cambiar o restablecer el prefijo",
        nuevo_prefix="Escribe el nuevo prefijo (solo si vas a cambiar)"
    )
    @app_commands.choices(accion=[
        app_commands.Choice(name="Cambiar", value="change"),
        app_commands.Choice(name="Restablecer", value="reset")
    ])
    # Solo usuarios con permiso de Administrador pueden usar esto
    @app_commands.checks.has_permissions(administrator=True)
    async def prefix(
        self, 
        interaction: discord.Interaction, 
        accion: app_commands.Choice[str], 
        nuevo_prefix: str = None
    ):
        guild_id = str(interaction.guild.id)
        
        # Cargar los prefijos actuales
        prefixes = {}
        if os.path.exists('prefixes.json'):
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)

        if accion.value == "change":
            if nuevo_prefix is None:
                return await interaction.response.send_message(
                    "❌ Debes especificar un nuevo prefijo.", ephemeral=True
                )
            
            if len(nuevo_prefix) > 5:
                return await interaction.response.send_message(
                    "❌ El prefijo es demasiado largo (máximo 5 caracteres).", ephemeral=True
                )

            prefixes[guild_id] = nuevo_prefix
            mensaje = f"✅ El prefijo ha sido cambiado a: `{nuevo_prefix}`"
        
        else: # Acción: Restablecer
            if guild_id in prefixes:
                del prefixes[guild_id]
                mensaje = "🔄 El prefijo ha sido restablecido al valor por defecto."
            else:
                return await interaction.response.send_message(
                    "ℹ️ El servidor ya está utilizando el prefijo por defecto.", ephemeral=True
                )

        # Guardar cambios en el JSON
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        # Crear un Embed elegante para la confirmación
        embed = discord.Embed(
            title="⚙️ Configuración de Prefijo",
            description=mensaje,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Cambio realizado por {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

    # Manejador de errores por si alguien sin permisos intenta usarlo
    @prefix.error
    async def prefix_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden cambiar el prefijo del bot.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(SetPrefix(bot))