import discord
from discord.ext import commands
from discord import app_commands

class Avatar(commands.Cog):
    """
    Cog optimizado para mostrar avatares con diseño limpio y color dinámico.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="avatar", 
        description="Muestra el avatar de un usuario en alta definición."
    )
    @app_commands.describe(usuario="El usuario objetivo (vacio para ver el tuyo)")
    async def avatar(self, ctx, usuario: discord.Member = None):
        """
        Extrae y muestra el avatar del usuario con integración de color de perfil.
        """
        await ctx.defer()

        # Determinamos el objetivo del comando
        target = usuario or ctx.author
        
        # Obtenemos la URL del avatar en 1024px (Máxima nitidez en Discord)
        avatar_url = target.display_avatar.with_size(1024).url

        # --- LÓGICA DE COLOR DINÁMICO ---
        # Si el usuario no tiene color en su rol, usamos un gris oscuro elegante (Sybaru Style)
        embed_color = target.color if target.color != discord.Color.default() else discord.Color.from_rgb(43, 45, 49)

        # Construcción del Embed
        embed = discord.Embed(
            title=f"👤 Avatar de {target.display_name}",
            url=avatar_url, # El título funciona como link directo a la imagen
            color=embed_color
        )
        
        # Imagen principal expandida
        embed.set_image(url=avatar_url)
        
        # Footer minimalista con la estética de Sybaru
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    """Registro del módulo Avatar en el sistema de Cogs."""
    await bot.add_cog(Avatar(bot))