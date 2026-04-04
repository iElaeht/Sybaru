import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import random

class Gifs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_key = os.getenv('GIPHY_TOKEN')

    @commands.hybrid_command(
        name="gif", 
        with_app_command=True, 
        description="Busca un gif aleatorio o de un tema específico"
    )
    @app_commands.describe(busqueda="¿Qué buscar? (Deja vacío para algo aleatorio)")
    async def gif(self, ctx, busqueda: str = None):
        """Muestra un gif de Giphy sin título para un diseño más limpio."""
        
        await ctx.defer()

        # Si no hay búsqueda, usamos el endpoint 'random' de Giphy
        if busqueda is None or busqueda.lower() in ["random", "aleatorio"]:
            url = f"https://api.giphy.com/v1/gifs/random?api_key={self.giphy_key}&tag=&rating=pg13"
            modo_busqueda = "Aleatorio"
        else:
            # Si hay búsqueda, usamos el endpoint 'search'
            url = f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_key}&q={busqueda}&limit=20&offset=0&rating=pg13&lang=es"
            modo_busqueda = busqueda

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extraer la URL según el modo (random y search devuelven estructuras diferentes)
                        if "random" in url:
                            url_gif = data['data']['images']['original']['url']
                        else:
                            gifs = data.get('data', [])
                            if not gifs:
                                return await ctx.send(f"❌ No encontré resultados para: `{busqueda}`")
                            seleccionado = random.choice(gifs)
                            url_gif = seleccionado['images']['original']['url']

                        # Creamos el Embed sin título para máxima limpieza
                        embed = discord.Embed(color=discord.Color.random())
                        embed.set_image(url=url_gif)
                        embed.set_footer(text=f"🔍: {modo_busqueda} | Solicitado por {ctx.author.name}")

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Hubo un problema al conectar con Giphy.")
        
        except Exception as e:
            print(f"Error en comando gif: {e}")
            await ctx.send("⚠️ Ocurrió un error inesperado.")

async def setup(bot):
    await bot.add_cog(Gifs(bot))