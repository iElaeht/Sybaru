import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils.uma_data import UMAS_LIST 

class UmaMusume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uma", description="¿Qué Umamusume te acompaña hoy?")
    async def uma(self, interaction: discord.Interaction):
        # Selección aleatoria
        uma = random.choice(UMAS_LIST)
        
        # Sistema de fortuna (Luck)
        fortunas = ["⭐ Gran Suerte", "✨ Suerte Media", "✅ Suerte Normal", "🍃 Suerte Modesta"]
        suerte = random.choice(fortunas)

        embed = discord.Embed(
            title="🏇 ¡Tu Umamusume del día!",
            description=f"Hoy el destino dice que corras con:\n# **{uma['name']}**",
            color=uma['color']
        )

        embed.add_field(name="🍀 Fortuna", value=suerte, inline=True)

        # Si ya pusiste la URL, la muestra. Si no, avisa.
        if "http" in uma['image']:
            embed.set_image(url=uma['image'])
        else:
            embed.set_footer(text="⚠️ Falta configurar la URL de la imagen.")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UmaMusume(bot))