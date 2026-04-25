import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import random

class Anime(commands.Cog):
    """
    Cog dedicado a la búsqueda de contenido visual de anime.
    Utiliza Nekos.best para resultados aleatorios y Giphy para búsquedas específicas.
    """
    def __init__(self, bot):
        self.bot = bot
        self.giphy_key = os.getenv('GIPHY_TOKEN')
        # Color rosa característico de la sección de anime de Sybaru
        self.color_anime = discord.Color.from_rgb(255, 105, 180)

    @commands.hybrid_command(
        name="gifanime", 
        description="Busca un gif de anime (Aleatorio o específico mediante búsqueda)"
    )
    @app_commands.describe(busqueda="Ej: 'Albedo Overlord', 'Sukuna' o vacío para algo al azar")
    async def gifanime(self, ctx, busqueda: str = None):
        """
        Lógica de búsqueda:
        1. Si no hay búsqueda: Consulta la API de Nekos.best (Gifs de alta calidad).
        2. Si hay búsqueda: Consulta Giphy con un filtro optimizado para evitar 'Live Action'.
        """
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            
            # --- CASO 1: BÚSQUEDA ALEATORIA (Nekos.best) ---
            if busqueda is None:
                url_nekos = "https://nekos.best/api/v2/smile?limit=20"
                try:
                    async with session.get(url_nekos, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            res = random.choice(data['results'])
                            # Terminamos la función enviando el resultado de Nekos
                            return await self._enviar_embed(ctx, res['url'], res.get('anime_name', 'Anime Aleatorio'))
                except Exception as e:
                    print(f"⚠️ Sybaru Log: Fallo Nekos.best ({e}), reintentando con Giphy...")
                    # No retornamos aquí para que, si falla Nekos, intente usar Giphy como respaldo

            # --- CASO 2: BÚSQUEDA ESPECÍFICA O RESPALDO (Giphy) ---
            # Optimizamos la query para forzar resultados de animación japonesa
            query_optimizada = f"anime {busqueda if busqueda else 'kawaii'} official scene"
            params = {
                "api_key": self.giphy_key,
                "q": query_optimizada,
                "limit": 25,
                "rating": "pg13"
            }

            try:
                async with session.get("https://api.giphy.com/v1/gifs/search", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gifs = data.get('data', [])

                        # Filtro de seguridad: Priorizamos resultados que contengan 'anime' o 'animation'
                        filtrados = [
                            g for g in gifs 
                            if "anime" in g.get('title', '').lower() 
                            or "animation" in g.get('title', '').lower()
                        ]

                        # Selección final: si el filtro es muy estricto, usamos la lista general saltando el primer resultado
                        finales = filtrados if len(filtrados) > 0 else gifs[1:]

                        if not finales:
                            return await ctx.send(f"❌ No pude encontrar nada relacionado con `{busqueda}`.")

                        # Seleccionamos un GIF al azar del Top 10 para dar variedad
                        seleccionado = random.choice(finales[:10])
                        url_gif = seleccionado['images']['original']['url']
                        
                        # Limpiamos el título quitando la coletilla " GIF" que pone Giphy
                        nombre = seleccionado.get('title', busqueda or "Anime").split(" GIF")[0]

                        await self._enviar_embed(ctx, url_gif, nombre)
                    else:
                        await ctx.send("⚠️ La base de datos de Giphy no responde.")
            except Exception as e:
                print(f"❌ Sybaru Log Error: {e}")
                await ctx.send("❌ Ocurrió un error inesperado al procesar la búsqueda.")

    async def _enviar_embed(self, ctx, url, nombre):
        """
        Función auxiliar para estandarizar el diseño de los embeds de anime.
        """
        embed = discord.Embed(color=self.color_anime)
        embed.set_image(url=url)
        # Footer personalizado con el autor y la fuente
        embed.set_footer(
            text=f"🌸 {nombre} | Solicitado por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

async def setup(bot):
    """Carga del Cog en el sistema central."""
    await bot.add_cog(Anime(bot))