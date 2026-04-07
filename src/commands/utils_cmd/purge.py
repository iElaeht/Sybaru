import discord
from discord.ext import commands
from discord import app_commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="purge", description="Elimina una cantidad de mensajes")
    @app_commands.describe(cantidad="¿Cuántos mensajes quieres borrar?")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, cantidad: int):
        await ctx.defer(ephemeral=True)

        if cantidad <= 0:
            return await ctx.send("❌ La cantidad debe ser mayor a 0.")

        limite = cantidad if ctx.interaction else cantidad + 1
        borrados = await ctx.channel.purge(limit=limite)
        
        await ctx.send(f"✅ Se han eliminado {len(borrados)} mensajes.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Purge(bot))