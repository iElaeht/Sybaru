import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="setprefix", 
        with_app_command=True, 
        description="Cambia el prefijo del bot para este servidor"
    )
    @app_commands.describe(nuevo_prefijo="El nuevo símbolo para los comandos (ejemplo: $, ., >)")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, nuevo_prefijo: str):
        """Cambia el prefijo del bot dinámicamente."""
        
        prefixes_file = 'prefixes.json'
        
        if os.path.exists(prefixes_file):
            with open(prefixes_file, 'r') as f:
                prefixes = json.load(f)
        else:
            prefixes = {}

        prefixes[str(ctx.guild.id)] = nuevo_prefijo

        with open(prefixes_file, 'w') as f:
            json.dump(prefixes, f, indent=4)

        await ctx.send(f"✅ El prefijo para este servidor ha sido cambiado a: `{nuevo_prefijo}`")

async def setup(bot):
    await bot.add_cog(Config(bot))