import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Purge(commands.Cog):
    """
    Cog de moderación básica para la limpieza de canales.
    Incluye protecciones contra abusos y límites de seguridad.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="purge", 
        description="Elimina mensajes del canal actual de forma masiva."
    )
    @app_commands.describe(cantidad="Número de mensajes a eliminar (Máximo 100)")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, cantidad: int):
        """
        Limpia el historial de mensajes. 
        Utiliza una respuesta efímera para no ensuciar el canal recién limpiado.
        """
        # Marcamos como efímero para que solo el moderador vea el proceso inicial
        await ctx.defer(ephemeral=True)

        # --- VALIDACIONES DE SEGURIDAD ---
        if cantidad <= 0:
            return await ctx.send("❌ La cantidad debe ser un número positivo.", ephemeral=True)
        
        if cantidad > 100:
            return await ctx.send("⚠️ Por seguridad, solo puedes borrar hasta 100 mensajes a la vez.", ephemeral=True)

        try:
            # Ajuste de límite: Si es comando de texto (!purge), sumamos 1 para borrar el mensaje del comando
            limite_real = cantidad if ctx.interaction else cantidad + 1
            
            # Ejecución de la purga
            borrados = await ctx.channel.purge(limit=limite_real)
            
            # Restamos 1 al conteo visual si fue comando de texto para que coincida con lo que pidió el usuario
            conteo_final = len(borrados) if ctx.interaction else len(borrados) - 1
            
            # Mensaje de confirmación (se borrará solo para mantener la limpieza)
            msg_confirmacion = f"🧹 **Limpieza completada:** Se han eliminado `{conteo_final}` mensajes."
            await ctx.send(msg_confirmacion, delete_after=7)

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para gestionar mensajes en este canal.")
        except discord.HTTPException as e:
            await ctx.send(f"⚠️ Hubo un error al intentar borrar los mensajes: {e}")

    @purge.error
    async def purge_error(self, ctx, error):
        """Manejo de errores específicos para el comando purge."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Necesitas el permiso `Gestionar Mensajes` para usar este comando.", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ ¡Ups! No puedo hacer la limpieza porque no tengo el permiso `Gestionar Mensajes`.", ephemeral=True)

async def setup(bot):
    """Carga del módulo de administración Purge."""
    await bot.add_cog(Purge(bot))