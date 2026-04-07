import discord
from discord.ext import commands
import aiohttp
import random

class Reacciones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color_embed = discord.Color.from_rgb(255, 182, 193)
        self.contadores = {}

    async def _enviar_reaccion(self, ctx, usuario_objetivo, endpoint, texto_accion, emoji, es_solo=False):
        """Función maestra para Nekos.best con soporte para múltiples acciones."""
        await ctx.defer()
        
        url = f"https://nekos.best/api/v2/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        resultado = data['results'][0]
                        url_gif = resultado['url']
                        nombre_anime = resultado.get('anime_name', 'Original')

                        if usuario_objetivo is None or usuario_objetivo == ctx.author:
                            descripcion = f"{emoji} **{ctx.author.name}** {es_solo}"
                        else:
                            key = (ctx.author.id, usuario_objetivo.id, endpoint)
                            self.contadores[key] = self.contadores.get(key, 0) + 1
                            veces = self.contadores[key]
                            extra = f" ¡Ya van **{veces}** veces!" if veces > 1 else ""
                            descripcion = f"{emoji} **{ctx.author.name}** ha {texto_accion} a **{usuario_objetivo.name}**.{extra}"

                        embed = discord.Embed(description=descripcion, color=self.color_embed)
                        embed.set_image(url=url_gif)
                        embed.set_footer(text=f"🎬 Anime: {nombre_anime} | Solicitado por {ctx.author.name}")
                        
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Sybaru no pudo conectar con la base de datos de anime.")
        except Exception as e:
            print(f"Error en Reacciones: {e}")
            await ctx.send("⚠️ Ocurrió un error al obtener la reacción.")

    # --- COMANDOS ORIGINALES ---
    @commands.hybrid_command(name="dance", description="Bailar con mucha energía")
    async def dance(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "dance", "bailado con", "💃", es_solo="está bailando muy alegre!")

    @commands.hybrid_command(name="slap", description="Dar una bofetada")
    async def slap(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "slap", "abofeteado", "👋", es_solo="lanza bofetadas al aire.")

    @commands.hybrid_command(name="hug", description="Dar un abrazo")
    async def hug(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "hug", "abrazado", "🫂", es_solo="se abraza a sí mismo.")

    @commands.hybrid_command(name="pat", description="Acariciar la cabeza")
    async def pat(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "pat", "acariciado", "🐱", es_solo="se da mimos solo.")

    @commands.hybrid_command(name="kiss", description="Dar un beso")
    async def kiss(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "kiss", "besado", "💋", es_solo="lanza un beso al viento.")

    # --- COMANDOS DE ACCIÓN Y ATAQUE ---
    @commands.hybrid_command(name="punch", description="Dar un puñetazo")
    async def punch(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "punch", "golpeado", "👊", es_solo="está golpeando sacos de boxeo.")

    @commands.hybrid_command(name="shoot", description="Disparar (de broma)")
    async def shoot(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "shoot", "disparado a", "🔫", es_solo="está practicando su puntería.")

    @commands.hybrid_command(name="yeet", description="Lanzar a alguien lejos")
    async def yeet(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "yeet", "lanzado por los aires a", "💨", es_solo="se lanzó al vacío!")

    # --- COMANDOS DE ESTADO Y EMOCIÓN ---
    @commands.hybrid_command(name="cry", description="Ponerse a llorar")
    async def cry(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "cry", "llorado con", "😭", es_solo="está llorando desconsoladamente.")

    @commands.hybrid_command(name="blush", description="Sonrojarse")
    async def blush(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "blush", "sonrojado por", "😳", es_solo="está muy sonrojado/a.")

    @commands.hybrid_command(name="pout", description="Hacer un berrinche/puchero")
    async def pout(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "pout", "hecho un puchero a", "😤", es_solo="está haciendo un berrinche.")

    @commands.hybrid_command(name="think", description="Quedarse pensando")
    async def think(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "think", "pensado profundamente en", "🤔", es_solo="está reflexionando sobre la vida.")

    # --- COMANDOS DE VIDA DIARIA ---
    @commands.hybrid_command(name="sleep", description="Irse a dormir")
    async def sleep(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "sleep", "dormido junto a", "😴", es_solo="se ha quedado profundamente dormido/a.")

    @commands.hybrid_command(name="eat", description="Comer algo rico")
    async def eat(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "feed", "alimentado a", "🍱", es_solo="está comiendo algo delicioso.")

    @commands.hybrid_command(name="wave", description="Saludar con la mano")
    async def wave(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "wave", "saludado a", "👋", es_solo="está saludando a todos!")

    @commands.hybrid_command(name="laugh", description="Reírse a carcajadas")
    async def laugh(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "laugh", "reído de", "🤣", es_solo="no puede parar de reír!")

async def setup(bot):
    await bot.add_cog(Reacciones(bot))