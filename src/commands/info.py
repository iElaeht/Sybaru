import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color_sybaru = discord.Color.from_rgb(255, 182, 193)

    @commands.hybrid_command(
        name="comandos", 
        description="Muestra la lista de comandos disponibles de Sybaru"
    )
    async def comandos(self, ctx):
        """Panel visual de todos los comandos de Sybaru."""
        
        embed = discord.Embed(
            title="🏮 Panel de Comandos de Sybaru",
            description=(
                "¡Hola! Soy **Sybaru**, tu asistente personal de Discord.\n"
                "Aquí tienes mi lista de funciones organizadas por categorías."
            ),
            color=self.color_sybaru
        )

        # Reacciones
        embed.add_field(
            name="🎭 Reacciones (Roleplay)",
            value=(
                "`dance`, `slap`, `hug`, `pat`, `kiss`, `bite`,\n"
                "`kick`, `poke`, `smile`, `punch`, `shoot`,\n"
                "`yeet`, `cry`, `blush`, `pout`, `think`,\n"
                "`sleep`, `eat`, `wave`, `laugh`"
            ),
            inline=False
        )

        # Anime
        embed.add_field(
            name="🌸 Anime & Media",
            value="`gifanime`: Busca GIFs aleatorios o de un anime específico.",
            inline=False
        )

        # Utilidad
        embed.add_field(
            name="🛠️ Utilidad & Info",
            value="`userinfo`: Datos de un usuario.\n`avatar`: Mira fotos de perfil.\n`purge`: Limpiar chat.",
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Sybaru Bot | Prefijo: /", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))