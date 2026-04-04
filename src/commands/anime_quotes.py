import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import random

class AnimeQuotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_key = os.getenv('GIPHY_TOKEN')
        # Frases de respaldo por si la API de internet falla
        self.respaldo = [
            {"content": "I will never go back on my word, because that is my ninja way!", "character": "Naruto Uzumaki", "anime": "Naruto"},
            {"content": "If you don't take risks, you can't create a future.", "character": "Monkey D. Luffy", "anime": "One Piece"},
            {"content": "The world isn't perfect. But it's there for us, doing the best it can.", "character": "Roy Mustang", "anime": "Fullmetal Alchemist"}
        ]

    @commands.hybrid_command(
        name="animefrase", 
        description="Obtén una frase de anime aleatoria (Con respaldo inteligente)"
    )
    async def animefrase(self, ctx):
        await ctx.defer()

        # Intentamos conectar con la API (Versión estable)
        quote_url = "https://animechan.io/api/v1/quotes/random"
        
        frase_en, personaje, serie = None, None, None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(quote_url, timeout=5) as quote_resp:
                    if quote_resp.status == 200:
                        data = await quote_resp.json()
                        # Estructura de la API nueva: data['data']
                        frase_en = data['data']['content']
                        personaje = data['data']['character']['name']
                        serie = data['data']['anime']['name']
                    else:
                        # Si la API responde error (500, 404, etc), usamos respaldo
                        cita = random.choice(self.respaldo)
                        frase_en, personaje, serie = cita["content"], cita["character"], cita["anime"]

                # Buscamos el GIF en Giphy
                query = f"{personaje} {serie} anime"
                giphy_url = f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_key}&q={query}&limit=5&rating=pg13"
                
                async with session.get(giphy_url) as gif_resp:
                    url_gif = None
                    if gif_resp.status == 200:
                        gif_data = await gif_resp.json()
                        gifs = gif_data.get('data', [])
                        if gifs:
                            url_gif = random.choice(gifs)['images']['original']['url']

                    # Construcción del Embed
                    embed = discord.Embed(
                        description=f"### \"{frase_en}\"",
                        color=discord.Color.from_rgb(147, 112, 219)
                    )
                    
                    if url_gif:
                        embed.set_image(url=url_gif)
                    
                    embed.set_footer(text=f"🎙️ {personaje} de {serie} | Solicitado por {ctx.author.name}")

                    await ctx.send(embed=embed)

        except Exception as e:
            # Si hay un error de conexión total (timeout), también usamos el respaldo
            print(f"Error de conexión: {e}. Usando frases de respaldo.")
            cita = random.choice(self.respaldo)
            await ctx.send(f"⚠️ La API está caída, pero aquí tienes una clásica:\n\n**\"{cita['content']}\"** - {cita['character']}")

async def setup(bot):
    await bot.add_cog(AnimeQuotes(bot))