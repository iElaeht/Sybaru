import discord
from discord.ext import commands

class Info(commands.Cog):
    """
    Cog informativo sobre las capacidades de Sybaru.
    Diseño visual optimizado para facilitar la navegación del usuario.
    """
    def __init__(self, bot):
        self.bot = bot
        # Un tono rosado pastel característico de Sybaru
        self.color_sybaru = discord.Color.from_rgb(255, 182, 193)

    @commands.hybrid_command(
        name="comandos", 
        description="Explora el catálogo completo de funciones de Sybaru."
    )
    async def comandos(self, ctx):
        """Muestra un panel organizado con todos los comandos disponibles."""
        
        embed = discord.Embed(
            title="🏮 Centro de Ayuda de Sybaru",
            description=(
                "¡Hola! Soy tu asistente multimedia y de entretenimiento.\n"
                "Usa `/` o el prefijo del servidor para interactuar conmigo.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=self.color_sybaru
        )

        # --- MÚSICA & PLAYLIST ---
        # Usamos bloques de código (`) para que los comandos resalten sobre el texto
        embed.add_field(
            name="🎵 Música & Entretenimiento",
            value=(
                "┕ `play`, `skip`, `stop`, `loop`, `queue`\n"
                "┕ `playlist_queue`, `playlist_remove`, `playlist_clear`"
            ),
            inline=False
        )

        # --- INTERACCIÓN ---
        embed.add_field(
            name="💘 Interacción & Anime",
            value=(
                "┕ `lovec`, `uma`, `gifanime`, `gif`, `animefrase`"
            ),
            inline=False
        )

        # --- ROLEPLAY ---
        # Dividido por categorías para no saturar una sola línea
        roleplay_content = (
            "⭐ **Social:** `hug`, `kiss`, `pat`, `cuddle`, `wave`\n"
            "💢 **Acción:** `slap`, `punch`, `kick`, `bite`, `yeet`\n"
            "☁️ **Estado:** `cry`, `smile`, `blush`, `laugh`, `sleep`"
        )
        embed.add_field(
            name="🎭 Reacciones & Roleplay",
            value=roleplay_content,
            inline=False
        )

        # --- UTILIDAD ---
        embed.add_field(
            name="🛠️ Sistema & Utilidad",
            value=(
                "┕ `setprefix`, `avatar`, `userinfo`, `infoserver`\n"
                "┕ `say`, `purge`, `comandos`"
            ),
            inline=False
        )

        # Estética final: Miniatura y Footer
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Un separador visual antes del footer
        embed.add_field(name="​", value="━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
        
        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name} | v1.2", 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    """Carga del módulo de información."""
    await bot.add_cog(Info(bot))