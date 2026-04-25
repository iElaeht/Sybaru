import discord
from discord.ext import commands
from discord import app_commands
import random

class LoveCalc(commands.Cog):
    """
    Cog de entretenimiento para calcular la compatibilidad entre usuarios.
    Utiliza un sistema de semillas basado en IDs para mantener resultados consistentes.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="lovec",
        description="Calcula el nivel de amor y compatibilidad entre dos personas."
    )
    @app_commands.describe(
        usuario1="Primer usuario a comparar",
        usuario2="Segundo usuario (por defecto eres tú)"
    )
    async def lovec(
        self, 
        interaction: discord.Interaction, 
        usuario1: discord.Member, 
        usuario2: discord.Member = None
    ):
        """Calcula un porcentaje de amor con una barra visual y veredicto."""
        # Si no se provee el segundo usuario, el autor es el protagonista
        usuario2 = usuario2 or interaction.user

        # Caso especial: Amor propio
        if usuario1.id == usuario2.id:
            return await interaction.response.send_message(
                "✨ **Amor propio:** Es el paso más importante, ¡te quieres un 100%! Pero intenta buscar a alguien más para este test.", 
                ephemeral=True
            )

        # --- LÓGICA DE PERSISTENCIA ---
        # Sumamos IDs para que el resultado sea el mismo siempre para la misma pareja
        combined_id = usuario1.id + usuario2.id
        random.seed(combined_id)
        porcentaje = random.randint(0, 100)
        random.seed() # IMPORTANTE: Resetear la semilla para no afectar otros comandos del bot

        # --- DISEÑO DE LA BARRA ---
        # Usamos 10 bloques para la barra visual
        llenos = round(porcentaje / 10)
        vacios = 10 - llenos
        barra = "❤️" * llenos + "🖤" * vacios

        # --- CONFIGURACIÓN DE VEREDICTO ---
        if porcentaje <= 20:
            mensaje = "Mejor sigan siendo solo conocidos... 💀"
            color = discord.Color.from_rgb(231, 76, 60) # Rojo Error
        elif porcentaje <= 50:
            mensaje = "Hay una chispa, pero le falta gasolina. ⚡"
            color = discord.Color.from_rgb(230, 126, 34) # Naranja
        elif porcentaje <= 85:
            mensaje = "¡Aquí hay tema! Deberían intentar una cita. 😏"
            color = discord.Color.from_rgb(241, 196, 15) # Dorado
        else:
            mensaje = "¡Almas gemelas! ¿Cuándo es la boda? 💍"
            color = discord.Color.from_rgb(255, 105, 180) # Rosa fuerte

        # --- CONSTRUCCIÓN DEL EMBED ---
        embed = discord.Embed(
            title="💘 Test de Compatibilidad",
            description=f"Calculando afinidad para:\n**{usuario1.display_name}** & **{usuario2.display_name}**",
            color=color
        )

        # Resultado principal en un campo destacado
        embed.add_field(
            name=f"Resultado: {porcentaje}%",
            value=f"{barra}\n\n**Veredicto de Sybaru:**\n> {mensaje}",
            inline=False
        )

        # Detalle visual: Mostramos el avatar del usuario1 como miniatura
        embed.set_thumbnail(url=usuario1.display_avatar.url)
        
        embed.set_footer(
            text=f"Solicitado por {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Carga del módulo LoveCalc."""
    await bot.add_cog(LoveCalc(bot))