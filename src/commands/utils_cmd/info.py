import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color_sybaru = discord.Color.from_rgb(255, 182, 193)

    @commands.hybrid_command(
        name="comandos", 
        description="Muestra la lista completa de comandos de Sybaru"
    )
    async def comandos(self, ctx):
        """Panel visual de todos los comandos de Sybaru."""
        
        embed = discord.Embed(
            title="🏮 Panel de Comandos de Sybaru",
            description=(
                "¡Hola! Soy **Sybaru**. Aquí tienes mis funciones actualizadas.\n"
                "Usa `/` para activar cualquier comando."
            ),
            color=self.color_sybaru
        )

        # --- SECCIÓN MÚSICA & PLAYLIST ---
        embed.add_field(
            name="🎵 Música & Playlist Personal",
            value=(
                "`play`: Reproduce música o carga tus favoritos (si no escribes nada).\n"
                "`skip`, `stop`, `loop`, `queue`: Control de reproducción.\n"
                "`playlist_queue`: Mira tu lista guardada (Modo Libro).\n"
                "`playlist_remove`: Borra una canción específica.\n"
                "`playlist_clear`: Vacía toda tu lista personal."
            ),
            inline=False
        )

        # --- SECCIÓN ENTRETENIMIENTO ---
        embed.add_field(
            name="🏇 Entretenimiento & Anime",
            value=(
                "`uma`: Descubre qué Umamusume te acompaña hoy.\n"
                "`gifanime`: Busca GIFs de anime (Giphy + Nekos.best)."
            ),
            inline=False
        )

        # --- SECCIÓN ROLEPLAY ---
        embed.add_field(
            name="🎭 Reacciones (Roleplay)",
            value=(
                "`dance`, `slap`, `hug`, `pat`, `kiss`, `bite`, `kick`, `poke`,\n"
                "`smile`, `punch`, `shoot`, `yeet`, `cry`, `blush`, `pout`,\n"
                "`think`, `sleep`, `eat`, `wave`, `laugh`"
            ),
            inline=False
        )

        # --- SECCIÓN UTILIDAD ---
        embed.add_field(
            name="🛠️ Utilidad & Sistema",
            value=(
                "`userinfo`: Datos de un usuario.\n"
                "`avatar`: Ver foto de perfil.\n"
                "`purge`: Limpieza de mensajes."
            ),
            inline=False
        )

        # Estética del Embed
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Sybaru Bot | Versión 2.0 Music & Umas", 
            icon_url=self.bot.user.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))