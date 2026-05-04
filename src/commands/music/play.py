import discord
import asyncio
import aiohttp
import re
from discord.ext import commands
from discord import app_commands
from src.utils.music_logic import MusicManager
from src.utils.database import get_playlist

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="play", 
        description="Reproduce música de YouTube, Playlists o tus favoritos guardados"
    )
    @app_commands.describe(
        buscar="Escribe el nombre de la canción o pega un link de YouTube",
        playlist="Carga tu lista de favoritos desde la base de datos"
    )
    @app_commands.choices(playlist=[
        app_commands.Choice(name="🌟 Cargar mis Favoritos", value="yes")
    ])
    async def play(
        self, 
        interaction: discord.Interaction, 
        buscar: str = None, 
        playlist: app_commands.Choice[str] = None
    ):
        """Maneja la entrada de música y coordina con el MusicManager de Sybaru."""
        
        await interaction.response.defer()

        # --- VALIDACIONES DE ESTADO ---
        if not interaction.user.voice:
            msg = await interaction.followup.send("❌ ¡Debes estar en un canal de voz para usar este comando!", ephemeral=True)
            await msg.delete(delay=15)
            return

        if not playlist and not buscar:
            msg = await interaction.followup.send("⚠️ **¿Qué quieres escuchar?** Escribe algo o elige tus favoritos.", ephemeral=True)
            await msg.delete(delay=15)
            return

        if not interaction.guild.voice_client:
            try:
                await interaction.user.voice.channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ No pude unirme al canal: {e}", ephemeral=True)
                return

        try:
            # Obtenemos la cola ANTES de añadir nada para calcular posiciones
            queue = self.manager.get_queue(interaction.guild_id)
            vc = interaction.guild.voice_client
            SYBARU_COLOR = discord.Color.from_rgb(43, 45, 49)

            # --- ESCENARIO 1: CARGAR FAVORITOS ---
            if playlist and playlist.value == "yes":
                canciones_db = get_playlist(interaction.user.id)
                if not canciones_db:
                    msg = await interaction.followup.send("📂 No tienes canciones en tu lista de favoritos todavía.", ephemeral=True)
                    await msg.delete(delay=15)
                    return
                
                posicion_inicio = len(queue) + 1
                for titulo, url in canciones_db:
                    queue.append({
                        'title': titulo, 
                        'webpage_url': url, 
                        'url': None, 
                        'requester': interaction.user.display_name, 
                        'thumbnail': None
                    })
                
                embed = discord.Embed(
                    title="🌟 Colección Personal Cargada",
                    description=f"Se han sumado **{len(canciones_db)}** temas a la lista.",
                    color=discord.Color.gold()
                )
                embed.add_field(name="📍 Inicio en", value=f"`Posición {posicion_inicio}`", inline=True)
                embed.add_field(name="📊 Total ahora", value=f"`{len(queue)} canciones`", inline=True)
                embed.set_footer(text=f"Sybaru Bot • Gestión de Base de Datos")
                await interaction.followup.send(embed=embed)

            # --- ESCENARIO 2: BÚSQUEDA O ENLACE ---
            elif buscar:
                resultados = await self.manager.buscar_info(buscar)
                
                if not resultados:
                    msg = await interaction.followup.send(f"❌ No encontré nada para: `{buscar}`", ephemeral=True)
                    await msg.delete(delay=15)
                    return

                # Calculamos cuántas canciones había antes
                en_cola_antes = len(queue)
                
                for track in resultados:
                    track['requester'] = interaction.user.display_name
                    queue.append(track)
                
                total_ahora = len(queue)
                embed = discord.Embed(color=SYBARU_COLOR)
                
                # A. Si es una lista de reproducción (varios resultados)
                if len(resultados) > 1:
                    embed.title = "📂 Lista de reproducción añadida"
                    embed.description = f"Se han sumado **{len(resultados)}** canciones."
                    embed.add_field(name="📊 Total en cola", value=f"`{total_ahora} temas`", inline=True)
                    embed.set_footer(text=f"Sybaru Bot • Posición final: {total_ahora}")
                
                # B. Si el bot YA está tocando (Se añade a la cola)
                elif vc.is_playing() or vc.is_paused():
                    track = resultados[0]
                    # La posición real es el total de la cola ahora mismo
                    pos_actual = total_ahora 
                    
                    embed.title = "⏳ Añadido a la cola"
                    embed.description = f"**[{track.get('title')}]({track.get('webpage_url')})**"
                    
                    # CORRECCIÓN: Ahora muestra "X de Total" correctamente
                    embed.add_field(
                        name="📍 Posición", 
                        value=f"`{pos_actual} de {total_ahora}`", 
                        inline=True
                    )
                    embed.add_field(
                        name="👤 Pedido por", 
                        value=f"`{interaction.user.display_name}`", 
                        inline=True
                    )
                    
                    if track.get('thumbnail'):
                        embed.set_thumbnail(url=track.get('thumbnail'))
                    embed.set_footer(text="Sybaru Music • Dale a la ⭐ para guardar")
                
                # C. Si el bot estaba libre (Reproducción inmediata)
                else:
                    track = resultados[0]
                    embed.title = "🎶 Reproduciendo ahora"
                    embed.description = f"**[{track.get('title')}]({track.get('webpage_url')})**"
                    embed.color = discord.Color.green()
                    
                    # Es la primera canción de la lista
                    embed.add_field(name="📍 Posición", value=f"`1 de {total_ahora}`", inline=True)
                    
                    if track.get('thumbnail'):
                        embed.set_thumbnail(url=track.get('thumbnail'))
                    embed.set_footer(text="Sybaru Bot • ¡Música maestro!")

                msg = await interaction.followup.send(embed=embed)
                await msg.delete(delay=30)

            # --- INICIO DEL REPRODUCTOR ---
            if not vc.is_playing() and not vc.is_paused():
                self.manager.play_next(interaction)

        except Exception as e:
            print(f"❌ Error crítico en comando Play de Sybaru: {e}")
            await interaction.followup.send(f"❌ Hubo un error al procesar la música.", ephemeral=True)

    # --- AUTOCOMPLETADO ---
    @play.autocomplete('buscar')
    async def buscar_autocomplete(self, interaction: discord.Interaction, current: str):
        if not current or len(current) < 3: 
            return []
        if current.startswith(('http', 'www')):
            return [app_commands.Choice(name="🔗 Enlace directo detectado", value=current)]
        try:
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={current}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        raw_data = await response.text()
                        suggestions = re.findall(r'\["([^"]+)"', raw_data)
                        return [app_commands.Choice(name=s[:100], value=s) for s in suggestions[1:11]]
        except: return []
        return []

async def setup(bot):
    await bot.add_cog(Play(bot))