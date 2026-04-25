import discord
from discord.ext import commands
import aiohttp

class Reacciones(commands.Cog):
    """
    Sistema de interacciones sociales y roleplay animado.
    Utiliza Nekos.best para obtener GIFs de alta calidad.
    """
    def __init__(self, bot):
        self.bot = bot
        # Color rosa pastel característico para las interacciones
        self.color_embed = discord.Color.from_rgb(255, 182, 193)
        # Diccionario para almacenar cuántas veces se han interactuado los usuarios
        self.contadores = {}

    async def _enviar_reaccion(self, ctx, usuario_objetivo, endpoint, texto_accion, emoji, es_solo=False):
        """
        Función maestra que procesa la petición a la API, gestiona el contador
        de interacciones y construye el Embed final.
        """
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

                        # Lógica de descripción: ¿Es una acción hacia otro o hacia uno mismo?
                        if usuario_objetivo is None or usuario_objetivo == ctx.author:
                            descripcion = f"{emoji} **{ctx.author.name}** {es_solo}"
                        else:
                            # Sistema de contadores persistente por sesión
                            key = (ctx.author.id, usuario_objetivo.id, endpoint)
                            self.contadores[key] = self.contadores.get(key, 0) + 1
                            veces = self.contadores[key]
                            extra = f" ¡Ya van **{veces}** veces!" if veces > 1 else ""
                            descripcion = f"{emoji} **{ctx.author.name}** ha {texto_accion} **{usuario_objetivo.name}**.{extra}"

                        # Construcción estética del Embed
                        embed = discord.Embed(description=descripcion, color=self.color_embed)
                        embed.set_image(url=url_gif)
                        embed.set_footer(text=f"🎬 Anime: {nombre_anime} | Solicitado por {ctx.author.name}")
                        
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"❌ Error de API: No se encontró contenido para `{endpoint}`.")
        except Exception as e:
            print(f"❌ Sybaru Log Error (Reacciones/{endpoint}): {e}")
            await ctx.send("⚠️ Sybaru no pudo obtener el GIF. Inténtalo de nuevo.")

    # ================================
    # CATEGORÍA: AFIRMACIÓN Y NEGACIÓN
    # ================================
    @commands.hybrid_command(name="si", description="Decir que sí con alegría")
    async def si(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "happy", "dicho que sí a", "✅", es_solo="dice que sí con mucha alegría!")

    @commands.hybrid_command(name="no", description="Decir que no o negarse")
    async def no(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "pout", "dicho que no a", "🚫", es_solo="se ha negado rotundamente.")

    # ================================
    # CATEGORÍA: INTERACCIÓN SOCIAL
    # ================================
    @commands.hybrid_command(name="hola", description="Saludar a alguien")
    async def hola(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "wave", "saludado a", "👋", es_solo="saluda a todo el servidor!")

    @commands.hybrid_command(name="hug", description="Dar un abrazo")
    async def hug(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "hug", "abrazado a", "🫂", es_solo="se abraza a sí mismo.")

    @commands.hybrid_command(name="kiss", description="Dar un beso")
    async def kiss(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "kiss", "besado a", "💋", es_solo="lanza un beso al aire.")

    @commands.hybrid_command(name="pat", description="Acariciar la cabeza")
    async def pat(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "pat", "acariciado a", "🐱", es_solo="se da mimos solo.")

    @commands.hybrid_command(name="cuddle", description="Acurrucarse")
    async def cuddle(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "cuddle", "acurrucado con", "🧣", es_solo="quiere cariñitos.")

    @commands.hybrid_command(name="handhold", description="Tomar de la mano")
    async def handhold(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "handhold", "tomado la mano de", "🤝", es_solo="quiere tomar la mano de alguien.")

    @commands.hybrid_command(name="highfive", description="Chocar esos cinco")
    async def highfive(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "highfive", "chocado los cinco con", "🙌", es_solo="busca a alguien para chocar los cinco.")

    @commands.hybrid_command(name="tickle", description="Hacer cosquillas")
    async def tickle(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "tickle", "hecho cosquillas a", "🤣", es_solo="se ríe solo de imaginarlo.")

    # ================================
    # CATEGORÍA: ACCIÓN Y COMBATE
    # ================================
    @commands.hybrid_command(name="slap", description="Dar una bofetada")
    async def slap(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "slap", "abofeteado a", "👋", es_solo="lanza bofetadas al aire.")

    @commands.hybrid_command(name="punch", description="Dar un puñetazo")
    async def punch(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "punch", "golpeado a", "👊", es_solo="entrena sus golpes.")

    @commands.hybrid_command(name="kick", description="Dar una patada")
    async def kick(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "kick", "dado una patada a", "🦵", es_solo="da patadas al aire.")

    @commands.hybrid_command(name="shoot", description="Disparar")
    async def shoot(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "shoot", "disparado a", "🔫", es_solo="está disparando al aire.")

    @commands.hybrid_command(name="yeet", description="Lanzar lejos")
    async def yeet(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "yeet", "lanzado por los aires a", "💨", es_solo="se lanzó al vacío!")

    @commands.hybrid_command(name="bite", description="Dar un mordisco")
    async def bite(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "bite", "mordido a", "🦷", es_solo="se muerde el labio.")

    @commands.hybrid_command(name="poke", description="Picar/Molestar")
    async def poke(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "poke", "picado a", "👉", es_solo="se pica a sí mismo.")

    # ================================
    # CATEGORÍA: EMOCIONES Y ESTADOS
    # ================================
    @commands.hybrid_command(name="cry", description="Llorar")
    async def cry(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "cry", "llorado junto a", "😭", es_solo="está llorando desconsoladamente.")

    @commands.hybrid_command(name="smile", description="Sonreír")
    async def smile(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "smile", "sonreído a", "😊", es_solo="tiene una gran sonrisa.")

    @commands.hybrid_command(name="blush", description="Sonrojarse")
    async def blush(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "blush", "sonrojado por", "😳", es_solo="está muy sonrojado/a.")

    @commands.hybrid_command(name="stare", description="Mirar fijamente")
    async def stare(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "stare", "mirado fijamente a", "👀", es_solo="se queda mirando fijamente.")

    @commands.hybrid_command(name="bored", description="Estar aburrido")
    async def bored(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "bored", "ignorado por aburrimiento a", "😴", es_solo="está muy aburrido.")

    @commands.hybrid_command(name="shrug", description="Encogerse de hombros")
    async def shrug(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "shrug", "encogido los hombros ante", "🤷", es_solo="no sabe qué decir.")

    @commands.hybrid_command(name="laugh", description="Reírse")
    async def laugh(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "laugh", "reído con", "🤣", es_solo="no puede parar de reír!")

    @commands.hybrid_command(name="think", description="Pensar")
    async def think(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "think", "pensado en", "🤔", es_solo="está reflexionando.")

    @commands.hybrid_command(name="lurk", description="Observar desde las sombras")
    async def lurk(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "lurk", "acechado a", "🕵️", es_solo="está observando desde las sombras...")

    # ================================
    # CATEGORÍA: DIVERSIÓN Y RUTINA
    # ================================
    @commands.hybrid_command(name="dance", description="Bailar")
    async def dance(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "dance", "bailado con", "💃", es_solo="baila con mucha alegría!")

    @commands.hybrid_command(name="eat", description="Comer algo")
    async def eat(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "feed", "alimentado a", "🍱", es_solo="está comiendo algo delicioso.")

    @commands.hybrid_command(name="sleep", description="Dormir")
    async def sleep(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "sleep", "dormido junto a", "😴", es_solo="se ha quedado dormido.")

    @commands.hybrid_command(name="nom", description="Comer/Morder cariñosamente")
    async def nom(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "nom", "dado un mordisquito a", "😋", es_solo="está comiendo un snack.")

    @commands.hybrid_command(name="headbang", description="Escuchar música a tope")
    async def headbang(self, ctx, usuario: discord.Member = None):
        await self._enviar_reaccion(ctx, usuario, "headbang", "rockeado con", "🤘", es_solo="está escuchando metal a tope!")

async def setup(bot):
    """Carga del módulo de Reacciones."""
    await bot.add_cog(Reacciones(bot))