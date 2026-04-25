import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class InfoServer(commands.Cog):
    """
    Cog informativo que despliega estadísticas técnicas del servidor.
    Diseñado para ofrecer una visión ejecutiva y limpia.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="infoserver",
        description="Muestra información detallada y profesional del servidor."
    )
    async def infoserver(self, interaction: discord.Interaction):
        """Genera un reporte técnico del servidor actual."""
        guild = interaction.guild
        
        # Fecha de creación con formato legible
        created_at = guild.created_at.strftime("%d/%m/%Y")
        
        # Cálculo de comunidad (Requiere Gateway Intents activos)
        total_members = guild.member_count
        bots = sum(1 for member in guild.members if member.bot) if guild.members else 0
        humans = total_members - bots

        # Conteo de canales por tipo
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        roles_count = len(guild.roles)

        # Configuración del diseño del Embed
        embed = discord.Embed(
            title=f"📊 Estadísticas: {guild.name}",
            description=f"Resumen técnico del servidor solicitado por {interaction.user.mention}.",
            color=discord.Color.from_rgb(43, 45, 49), # Gris oscuro premium
            timestamp=datetime.now()
        )

        # Icono del servidor (Thumbnail)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # --- SECCIÓN: IDENTIDAD ---
        identidad = (
            f"**ID:** `{guild.id}`\n"
            f"**Dueño:** {guild.owner.mention}\n"
            f"**Creado:** {created_at}"
        )
        embed.add_field(name="📌 Identidad", value=identidad, inline=True)

        # --- SECCIÓN: COMUNIDAD ---
        comunidad = (
            f"**Total:** `{total_members}`\n"
            f"👤 **Humanos:** `{humans}`\n"
            f"🤖 **Bots:** `{bots}`"
        )
        embed.add_field(name="👥 Comunidad", value=comunidad, inline=True)

        # --- SECCIÓN: RECURSOS ---
        recursos = (
            f"**Canales:** `{text_channels + voice_channels}`\n"
            f"**Roles:** `{roles_count}`\n"
            f"**Boosts:** `{guild.premium_subscription_count}` (Lvl {guild.premium_tier})"
        )
        embed.add_field(name="📂 Recursos", value=recursos, inline=True)

        # Imagen del banner (si el servidor tiene nivel de boost suficiente)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # Footer minimalista
        embed.set_footer(
            text=f"Sybaru System • {guild.name}", 
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Carga del módulo InfoServer."""
    await bot.add_cog(InfoServer(bot))