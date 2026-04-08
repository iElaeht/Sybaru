import discord
from discord.ext import commands
from discord import app_commands
import random

class LoveCalc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="lovec",
        description="Calcula la compatibilidad amorosa entre dos usuarios"
    )
    @app_commands.describe(
        usuario1="Primer usuario a comparar",
        usuario2="Segundo usuario (opcional, por defecto eres tú)"
    )
    async def lovec(
        self, 
        interaction: discord.Interaction, 
        usuario1: discord.Member, 
        usuario2: discord.Member = None
    ):
        # Si no se provee el segundo usuario, se usa a quien ejecutó el comando
        if usuario2 is None:
            usuario2 = interaction.user

        # Evitar calcular el amor con uno mismo de forma aburrida
        if usuario1.id == usuario2.id:
            return await interaction.response.send_message(
                "¡No puedes medir el amor contigo mismo! Quiérete mucho, pero elige a alguien más. ✨", 
                ephemeral=True
            )

        # Lógica para que el porcentaje sea "fijo" por pareja (basado en IDs)
        # Esto evita que el porcentaje cambie cada vez que se usa el comando
        combined_id = usuario1.id + usuario2.id
        random.seed(combined_id)
        porcentaje = random.randint(0, 100)
        random.seed() # Resetear la semilla para otros comandos

        # Crear la barra de corazones (10 bloques en total)
        corazones_llenos = round(porcentaje / 10)
        corazones_vacios = 10 - corazones_llenos
        barra = "❤️" * corazones_llenos + "🖤" * corazones_vacios

        # Determinar mensaje y color según el porcentaje
        if porcentaje <= 20:
            mensaje = "Mejor sigan siendo solo conocidos... 💀"
            color = discord.Color.red()
            emoji_central = "💔"
        elif porcentaje <= 50:
            mensaje = "Hay una chispa, pero le falta gasolina. ⚡"
            color = discord.Color.orange()
            emoji_central = "⚖️"
        elif porcentaje <= 85:
            mensaje = "¡Aquí hay tema! Deberían intentar una cita. 😏"
            color = discord.Color.gold()
            emoji_central = "🔥"
        else:
            mensaje = "¡Almas gemelas! ¿Cuándo es la boda? 💍"
            color = discord.Color.from_rgb(255, 105, 180) # Rosa fuerte
            emoji_central = "💖"

        # Crear el Embed profesional
        embed = discord.Embed(
            title="💘 Test de Compatibilidad",
            description=f"Calculando afinidad entre\n**{usuario1.display_name}** y **{usuario2.display_name}**",
            color=color
        )

        embed.add_field(
            name=f"Resultado: {porcentaje}%",
            value=f"{barra}\n\n**Veredicto:**\n{mensaje}",
            inline=False
        )

        # Miniatura con el emoji central grande
        embed.set_footer(text="Sybaru Love System • Resultados definitivos")
        
        # Enviar el resultado (Público para que todos vean el chisme)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LoveCalc(bot))