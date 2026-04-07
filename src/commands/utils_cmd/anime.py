import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import random

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_key = os.getenv('GIPHY_TOKEN')
        self.color_anime = discord.Color.from_rgb(255, 105, 180)

    @commands.hybrid_command(
        name="gifanime", 
        description="Busca un gif de anime (Aleatorio o específico)"
    )
    @app_commands.describe(busqueda="Ej: 'Albedo Overlord', 'Sukuna' o vacío para algo al azar")
    async def gifanime(self, ctx, busqueda: str = None):
        """Lógica dual: Nekos para aleatorio, Giphy filtrado para específico."""
        await ctx.defer()

        # --- CASO 1: ALEATORIO (Nekos.best) ---
        if busqueda is None:
            url_nekos = "https://nekos.best/api/v2/smile?limit=20" # 'smile' es muy variado
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_nekos) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            res = random.choice(data['results'])
                            return await self._enviar_embed(ctx, res['url'], res.get('anime_name', 'Anime Aleatorio'))
            except:
                pass # Si falla Nekos, intentamos Giphy abajo

        # --- CASO 2: ESPECÍFICO (Giphy con Super Filtro) ---
        # "Inyectamos" términos de búsqueda que Giphy solo usa para anime real
        query_optimizada = f"anime {busqueda} official scene"
        url_giphy = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": self.giphy_key,
            "q": query_optimizada,
            "limit": 25,
            "rating": "pg13"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url_giphy, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gifs = data.get('data', [])

                        # Filtramos para asegurar que sea animación
                        # (Buscamos que 'anime' esté en el título del GIF)
                        filtrados = [
                            g for g in gifs 
                            if "anime" in g.get('title', '').lower() 
                            or "animation" in g.get('title', '').lower()
                        ]

                        # Si no hay filtrados, usamos los resultados originales pero saltamos el primero
                        finales = filtrados if len(filtrados) > 0 else gifs[1:]

                        if not finales:
                            return await ctx.send(f"❌ No encontré nada para `{busqueda}`.")

                        # Elegimos uno al azar de los mejores resultados
                        seleccionado = random.choice(finales[:10])
                        url_gif = seleccionado['images']['original']['url']
                        
                        # Limpiamos el nombre para el footer
                        nombre = seleccionado.get('title', busqueda).split(" GIF")[0]

                        await self._enviar_embed(ctx, url_gif, nombre)
                    else:
                        await ctx.send("⚠️ Error al conectar con la base de datos.")
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("❌ Ocurrió un error en la búsqueda.")

    async def _enviar_embed(self, ctx, url, nombre):
        """Función auxiliar para mantener el diseño limpio."""
        embed = discord.Embed(color=self.color_anime)
        embed.set_image(url=url)
        embed.set_footer(text=f"🌸 Fuente: {nombre} | {ctx.author.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Anime(bot))