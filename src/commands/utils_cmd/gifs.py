import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import random

class Gifs(commands.Cog):
    """
    Cog para la búsqueda y visualización de GIFs mediante la API de Giphy.
    Diseño minimalista y optimizado para Sybaru.
    """
    def __init__(self, bot):
        self.bot = bot
        self.giphy_key = os.getenv('GIPHY_TOKEN')
        # Color oficial para comandos generales
        self.color_default = discord.Color.from_rgb(43, 45, 49) 

    @commands.hybrid_command(
        name="gif", 
        description="Busca un gif aleatorio o de un tema específico."
    )
    @app_commands.describe(busqueda="¿Qué buscar? (Vacio para algo aleatorio)")
    async def gif(self, ctx, busqueda: str = None):
        """
        Muestra un GIF en un diseño limpio sin títulos innecesarios.
        Maneja tanto búsquedas aleatorias como filtradas.
        """
        await ctx.defer()

        # Determinamos el modo de búsqueda para el footer
        modo_busqueda = busqueda if busqueda else "Aleatorio"
        
        # Preparamos la URL base
        if not busqueda:
            url = "https://api.giphy.com/v1/gifs/random"
            params = {"api_key": self.giphy_key, "tag": "", "rating": "pg13"}
        else:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": self.giphy_key, 
                "q": busqueda, 
                "limit": 20, 
                "rating": "pg13", 
                "lang": "es"
            }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extraer la URL (Giphy cambia la estructura entre 'random' y 'search')
                        if not busqueda:
                            url_gif = data['data']['images']['original']['url']
                        else:
                            gifs = data.get('data', [])
                            if not gifs:
                                return await ctx.send(f"❌ No encontré resultados para: `{busqueda}`", ephemeral=True)
                            
                            # Elegimos uno al azar del top para evitar que siempre salga el mismo
                            seleccionado = random.choice(gifs[:10])
                            url_gif = seleccionado['images']['original']['url']

                        # --- CONSTRUCCIÓN DEL EMBED MINIMALISTA ---
                        embed = discord.Embed(color=self.color_default)
                        embed.set_image(url=url_gif)
                        
                        # El footer ahora es más visual e informativo
                        embed.set_footer(
                            text=f"🔍 Búsqueda: {modo_busqueda.capitalize()} | {ctx.author.display_name}",
                            icon_url=ctx.author.display_avatar.url
                        )

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Error: No se pudo conectar con el servicio de Giphy.")
        
        except Exception as e:
            print(f"❌ Sybaru Log Error (GIF): {e}")
            await ctx.send("⚠️ Ocurrió un fallo al procesar el GIF.")

async def setup(bot):
    """Carga del módulo de GIFs."""
    await bot.add_cog(Gifs(bot))