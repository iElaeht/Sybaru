import discord
from discord.ext import commands
import os
import aiohttp
import random

class AnimeQuotes(commands.Cog):
    """
    Cog especializado en la obtención de frases célebres de anime.
    Incluye un sistema de respaldo (fail-safe) por si las APIs externas fallan.
    """
    def __init__(self, bot):
        self.bot = bot
        # Obtenemos el token de Giphy desde las variables de entorno
        self.giphy_key = os.getenv('GIPHY_TOKEN')
        
        # Lista de frases de respaldo para garantizar que el comando siempre responda
        self.respaldo = [
            {"content": "I will never go back on my word, because that is my ninja way!", "character": "Naruto Uzumaki", "anime": "Naruto"},
            {"content": "If you don't take risks, you can't create a future.", "character": "Monkey D. Luffy", "anime": "One Piece"},
            {"content": "The world isn't perfect. But it's there for us, doing the best it can.", "character": "Roy Mustang", "anime": "Fullmetal Alchemist"},
            {"content": "Whatever you lose, you'll find it again. But what you throw away you'll never get back.", "character": "Himura Kenshin", "anime": "Rurouni Kenshin"}
        ]

    @commands.hybrid_command(
        name="animefrase", 
        description="Obtén una frase de anime aleatoria con un GIF relacionado."
    )
    async def animefrase(self, ctx):
        """
        Comando híbrido que consulta la API de AnimeChan para obtener frases.
        Luego busca un GIF en Giphy basado en el personaje y la serie.
        """
        await ctx.defer() # Evitamos el error de 'interaction failed' por tiempo de espera

        # Endpoint de la API (Versión estable v1)
        quote_url = "https://animechan.io/api/v1/quotes/random"
        
        # Inicializamos variables por defecto
        frase_en, personaje, serie = None, None, None
        url_gif = None

        async with aiohttp.ClientSession() as session:
            # --- FASE 1: Obtención de la Frase ---
            try:
                async with session.get(quote_url, timeout=5) as quote_resp:
                    if quote_resp.status == 200:
                        data = await quote_resp.json()
                        # Estructura de datos según la documentación de AnimeChan v1
                        frase_en = data['data']['content']
                        personaje = data['data']['character']['name']
                        serie = data['data']['anime']['name']
                    else:
                        raise Exception("Status code no es 200")
            except Exception as e:
                # Si falla la API, seleccionamos una frase de nuestra lista local
                print(f"⚠️ Sybaru Log: Fallo en API AnimeChan. Motivo: {e}")
                cita = random.choice(self.respaldo)
                frase_en, personaje, serie = cita["content"], cita["character"], cita["anime"]

            # --- FASE 2: Obtención del GIF (Opcional) ---
            if self.giphy_key:
                try:
                    # Query optimizada para mejores resultados en Giphy
                    query = f"{personaje} {serie} anime"
                    giphy_url = f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_key}&q={query}&limit=5&rating=pg13"
                    
                    async with session.get(giphy_url) as gif_resp:
                        if gif_resp.status == 200:
                            gif_data = await gif_resp.json()
                            gifs = gif_data.get('data', [])
                            if gifs:
                                # Elegimos un GIF al azar de los primeros 5 resultados
                                url_gif = random.choice(gifs)['images']['original']['url']
                except Exception as e:
                    print(f"⚠️ Sybaru Log: Error buscando GIF. Motivo: {e}")

        # --- FASE 3: Construcción y Envío del Embed ---
        embed = discord.Embed(
            description=f"### \"{frase_en}\"",
            color=discord.Color.from_rgb(147, 112, 219) # Púrpura suave
        )
        
        if url_gif:
            embed.set_image(url=url_gif)
        
        embed.set_footer(
            text=f"🎙️ {personaje} • {serie} | Pedido por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    """Función obligatoria para que el bot cargue el Cog correctamente."""
    await bot.add_cog(AnimeQuotes(bot))