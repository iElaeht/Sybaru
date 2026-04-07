import discord
from discord.ext import commands
from discord import app_commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Muestra el avatar de un usuario")
    @app_commands.describe(usuario="El usuario del que quieres ver la foto")
    async def avatar(self, ctx, usuario: discord.Member = None):
        # Si 'usuario' no se elige, usamos al autor
        objetivo = usuario or ctx.author
        
        embed = discord.Embed(
            title=f"Avatar de {objetivo.name}", 
            color=discord.Color.blue()
        )
        embed.set_image(url=objetivo.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))