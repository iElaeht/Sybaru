import discord
from discord.ext import commands
from discord import app_commands

class Usuario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color_perfil = discord.Color.from_rgb(46, 204, 113) # Verde esmeralda

    @commands.hybrid_command(
        name="userinfo", 
        description="Muestra información detallada de un usuario"
    )
    @app_commands.describe(usuario="El usuario del que quieres saber más")
    async def userinfo(self, ctx, usuario: discord.Member = None):
        """Muestra el perfil detallado de un miembro del servidor."""
        objetivo = usuario or ctx.author
        
        # Formatear fechas
        creacion = objetivo.created_at.strftime("%d/%m/%Y")
        union = objetivo.joined_at.strftime("%d/%m/%Y")
        roles = [role.mention for role in objetivo.roles[1:]] 
        
        embed = discord.Embed(title=f"👤 Perfil de {objetivo.name}", color=self.color_perfil)
        embed.set_thumbnail(url=objetivo.display_avatar.url)
        
        embed.add_field(name="🆔 ID", value=f"`{objetivo.id}`", inline=True)
        embed.add_field(name="📅 Cuenta creada", value=creacion, inline=True)
        embed.add_field(name="📥 Ingreso al servidor", value=union, inline=True)
        
        # Si tiene demasiados roles, Discord da error. Limitamos a los más importantes.
        if roles:
            valor_roles = " ".join(roles[:15]) + ("..." if len(roles) > 15 else "")
        else:
            valor_roles = "Ninguno"
            
        embed.add_field(name="🎭 Roles", value=valor_roles, inline=False)
        embed.set_footer(text=f"Consultado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Usuario(bot))