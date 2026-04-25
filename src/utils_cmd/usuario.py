import discord
from discord.ext import commands
from discord import app_commands

class Usuario(commands.Cog):
    """
    Cog encargado de gestionar la información de los miembros.
    Proporciona un vistazo detallado a la identidad de los usuarios en el servidor.
    """
    def __init__(self, bot):
        self.bot = bot
        # Verde esmeralda para una sensación de frescura y perfil activo
        self.color_perfil = discord.Color.from_rgb(46, 204, 113)

    @commands.hybrid_command(
        name="userinfo", 
        description="Despliega el perfil técnico y social de un miembro."
    )
    @app_commands.describe(usuario="Selecciona al usuario (vacío para ver tu propio perfil)")
    async def userinfo(self, ctx, usuario: discord.Member = None):
        """Genera una tarjeta informativa con los datos del miembro seleccionado."""
        
        # Si no se menciona a nadie, el objetivo es quien ejecuta el comando
        objetivo = usuario or ctx.author
        
        # Formateo de fechas con estilo limpio
        creacion = objetivo.created_at.strftime("%d/%m/%Y")
        union = objetivo.joined_at.strftime("%d/%m/%Y")
        
        # Gestión de roles (excluyendo @everyone)
        roles = [role.mention for role in objetivo.roles[1:]]
        roles.reverse() # Los roles más altos primero
        
        # Identificación de tipo de cuenta
        tipo_cuenta = "🤖 Bot" if objetivo.bot else "👤 Humano"

        # --- CONSTRUCCIÓN DEL EMBED ---
        embed = discord.Embed(
            title=f"Información de Usuario: {objetivo.display_name}", 
            color=self.color_perfil
        )
        embed.set_thumbnail(url=objetivo.display_avatar.url)
        
        # Sección de Identidad
        embed.add_field(name="📌 Identidad", value=f"**ID:** `{objetivo.id}`\n**Tipo:** {tipo_cuenta}", inline=True)
        embed.add_field(name="👑 Rol Superior", value=objetivo.top_role.mention, inline=True)
        
        # Sección de Fechas
        embed.add_field(name="📅 Cuenta Creada", value=f"`{creacion}`", inline=True)
        embed.add_field(name="📥 Ingreso", value=f"`{union}`", inline=True)
        
        # Sección de Roles con protección de caracteres
        if roles:
            # Discord tiene un límite de 1024 caracteres por campo, limitamos a 15 roles para seguridad
            valor_roles = " ".join(roles[:15]) + ("..." if len(roles) > 15 else "")
        else:
            valor_roles = "Este usuario no tiene roles asignados."
            
        embed.add_field(name=f"🎭 Roles ({len(roles)})", value=valor_roles, inline=False)
        
        # Banner de perfil (si el usuario tiene uno configurado y el bot puede verlo)
        if hasattr(objetivo, 'banner') and objetivo.banner:
            embed.set_image(url=objetivo.banner.url)
            
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}", 
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Carga del módulo de información de usuario."""
    await bot.add_cog(Usuario(bot))