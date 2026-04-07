import discord
from discord.ext import commands
from discord import app_commands
from src.utils.music_logic import MusicManager, ytdl 
from src.utils.database import get_playlist
import asyncio
import aiohttp
import re

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="play", 
        description="Reproduce música, links de YouTube (incluye Playlists) o tus favoritos"
    )
    @app_commands.describe(
        buscar="Escribe el nombre de la canción o pega un link (YouTube/Playlist)",
        playlist="Selecciona para cargar tus favoritos de la base de datos"
    )
    @app_commands.choices(playlist=[
        app_commands.Choice(name="Cargar mis Favoritos 🌟", value="yes")
    ])
    async def play(
        self, 
        interaction: discord.Interaction, 
        buscar: str = None, 
        playlist: app_commands.Choice[str] = None
    ):
        """Controlador de reproducción con mensajes temporales y privados para errores."""
        await interaction.response.defer()

        # --- ERROR: NO ESTÁ EN CANAL DE VOZ ---
        if not interaction.user.voice:
            msg = await interaction.followup.send("❌ ¡Debes estar en un canal de voz!", ephemeral=True)
            await msg.delete(delay=30)
            return

        # --- ERROR: NADA QUE BUSCAR ---
        if not playlist and not buscar:
            msg = await interaction.followup.send("⚠️ **Necesitas escribir algo en 'buscar' o elegir tu playlist.**", ephemeral=True)
            await msg.delete(delay=30)
            return

        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()

        try:
            queue = self.manager.get_queue(interaction.guild_id)

            # --- CASO A: FAVORITOS ---
            if playlist and playlist.value == "yes":
                canciones_db = get_playlist(interaction.user.id)
                if not canciones_db:
                    msg = await interaction.followup.send("📂 Tu playlist personal está vacía.", ephemeral=True)
                    await msg.delete(delay=30)
                    return
                
                for titulo, url in canciones_db:
                    queue.append({
                        'title': titulo, 
                        'webpage_url': url, 
                        'url': None, 
                        'requester': interaction.user.display_name, 
                        'thumbnail': None
                    })
                # Confirmación de carga (puede ser pública o privada, aquí la puse temporal)
                msg = await interaction.followup.send(f"🌟 **Favoritos:** Cargando {len(canciones_db)} temas.")
                await msg.delete(delay=30)

            # --- CASO B: BÚSQUEDA O URL ---
            elif buscar:
                resultados = await self.manager.buscar_info(buscar)
                
                if not resultados:
                    msg = await interaction.followup.send(f"❌ No encontré resultados para: `{buscar}`", ephemeral=True)
                    await msg.delete(delay=30)
                    return

                for track in resultados:
                    track['requester'] = interaction.user.display_name
                    queue.append(track)
                
                if len(resultados) > 1:
                    msg = await interaction.followup.send(f"✅ **Playlist:** Se añadieron {len(resultados)} canciones.")
                    await msg.delete(delay=30)
                else:
                    titulo = resultados[0].get('title', 'Canción')
                    # Mensaje de "Añadido" o "Reproduciendo" temporal
                    msg = await interaction.followup.send(f"✅ **Añadido a la cola:** {titulo}")
                    await msg.delete(delay=30)

            # Lanzar el reproductor
            vc = interaction.guild.voice_client
            if not vc.is_playing() and not vc.is_paused():
                self.manager.play_next(interaction)

        except Exception as e:
            print(f"Error en Play Command: {e}")
            msg = await interaction.followup.send(f"❌ Error al procesar la música: {e}", ephemeral=True)
            await msg.delete(delay=30)

    # --- AUTOCOMPLETE (Se mantiene igual) ---
    @play.autocomplete('buscar')
    async def buscar_autocomplete(self, interaction: discord.Interaction, current: str):
        if not current or len(current) < 3: return []
        if current.startswith(('http', 'www')):
            return [app_commands.Choice(name="🔗 Enlace de YouTube detectado", value=current)]
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