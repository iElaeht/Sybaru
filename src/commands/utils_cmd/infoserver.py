import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class InfoServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="infoserver",
        description="Muestra información detallada y profesional del servidor"
    )
    async def infoserver(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Formatear la fecha de creación
        created_at = guild.created_at.strftime("%d/%m/%Y")
        
        # Contadores de miembros
        total_members = guild.member_count
        # Filtramos bots si quieres precisión (opcional)
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots

        # Canales
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        # Diseño del Embed
        embed = discord.Embed(
            title=f"📊 Información de {guild.name}",
            description=f"Aquí tienes los detalles técnicos del servidor **{guild.name}**.",
            color=discord.Color.from_rgb(43, 45, 49), # Color oscuro profesional
            timestamp=datetime.now()
        )

        # Miniatura del servidor (icono)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Campos de información general
        embed.add_field(name="👑 Dueño", value=f"{guild.owner.mention}", inline=True)
        embed.add_field(name="🆔 ID del Servidor", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 Creación", value=f"{created_at}", inline=True)

        # Campos de comunidad
        embed.add_field(
            name="👥 Usuarios", 
            value=f"Total: **{total_members}**\n👤 Humanos: {humans}\n🤖 Bots: {bots}", 
            inline=True
        )
        embed.add_field(
            name="💬 Canales", 
            value=f"📁 Categorías: {categories}\n📝 Texto: {text_channels}\n🔊 Voz: {voice_channels}", 
            inline=True
        )
        embed.add_field(
            name="✨ Mejoras (Boosts)", 
            value=f"Nivel: **{guild.premium_tier}**\nMejoras: **{guild.premium_subscription_count}**", 
            inline=True
        )

        # Imagen del banner si tiene
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.set_footer(
            text=f"Solicitado por {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )

        # Enviamos la respuesta (puedes poner ephemeral=True si prefieres que sea privado)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoServer(bot))