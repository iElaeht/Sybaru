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
                "¡Hola! Soy **Sybaru**. Aquí tienes mi catálogo de funciones actualizado.\n"
                "Usa `/` para comandos de barra o el prefijo configurado para texto."
            ),
            color=self.color_sybaru
        )

        # --- MÚSICA & FAVORITOS ---
        embed.add_field(
            name="🎵 Música & Playlist",
            value=(
                "`play`: Reproduce música o carga tus favoritos.\n"
                "`skip`, `stop`, `loop`, `queue`: Control de la cola.\n"
                "`playlist_queue`, `playlist_remove`, `playlist_clear`: Gestión de favoritos."
            ),
            inline=False
        )

        # --- INTERACCIÓN & DIVERSIÓN ---
        embed.add_field(
            name="💘 Interacción & Diversión",
            value=(
                "`lovec`: Compatibilidad entre usuarios.\n"
                "`uma`: Tu Umamusume diaria.\n"
                "`gifanime`: Buscador de GIFs de alta calidad.\n"
                "`gif`: Busca cualquier GIF en Giphy."
            ),
            inline=False
        )

        # --- ROLEPLAY (COMPLETO) ---
        embed.add_field(
            name="🎭 Reacciones & Roleplay",
            value=(
                "**Social:** `si`, `no`, `hola`, `hug`, `kiss`, `pat`, `cuddle`, `handhold`, `wave`\n"
                "**Acción:** `slap`, `punch`, `kick`, `shoot`, `yeet`, `bite`, `poke`\n"
                "**Estado:** `cry`, `smile`, `blush`, `stare`, `bored`, `shrug`, `laugh`, `sleep`, `think`\n"
                "**Otros:**  `eat`"
            ),
            inline=False
        )

        # --- UTILIDAD & PERSONALIZACIÓN ---
        embed.add_field(
            name="🛠️ Utilidad & Sistema",
            value=(
                "`prefix`: Cambia o restablece el prefijo del bot.\n"
                "`userinfo`: Datos detallados de un usuario.\n"
                "`avatar`: Muestra la foto de perfil en HD.\n"
                "`infoserver`: Estadísticas del servidor.\n"
                "`say`: El bot repite tu mensaje.\n"
                "`purge`: Limpia el historial de mensajes."
            ),
            inline=False
        )

        # Estética del Embed
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Sybaru Bot • Desarrollado por Elaehtdev", 
            icon_url=self.bot.user.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))