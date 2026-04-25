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
        # Nos aseguramos de que el bot tenga una instancia única del MusicManager
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
        """Maneja la entrada de música y coordina con el MusicManager."""
        
        # Defer para darle tiempo al bot de procesar links pesados o búsquedas
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

        # Conexión automática al canal de voz si no está conectado
        if not interaction.guild.voice_client:
            try:
                await interaction.user.voice.channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ No pude unirme al canal: {e}", ephemeral=True)
                return

        try:
            queue = self.manager.get_queue(interaction.guild_id)

            # --- ESCENARIO 1: CARGAR FAVORITOS ---
            if playlist and playlist.value == "yes":
                canciones_db = get_playlist(interaction.user.id)
                if not canciones_db:
                    msg = await interaction.followup.send("📂 No tienes canciones en tu lista de favoritos todavía.", ephemeral=True)
                    await msg.delete(delay=15)
                    return
                
                for titulo, url in canciones_db:
                    queue.append({
                        'title': titulo, 
                        'webpage_url': url, 
                        'url': None, 
                        'requester': interaction.user.display_name, 
                        'thumbnail': None
                    })
                
                msg = await interaction.followup.send(f"🌟 **Playlist Personal:** Se han añadido **{len(canciones_db)}** temas a la cola.")
                await msg.delete(delay=20)

            # --- ESCENARIO 2: BÚSQUEDA O ENLACE ---
            elif buscar:
                # Usamos el manager para extraer info de YouTube
                resultados = await self.manager.buscar_info(buscar)
                
                if not resultados:
                    msg = await interaction.followup.send(f"❌ No encontré nada para: `{buscar}`", ephemeral=True)
                    await msg.delete(delay=15)
                    return

                # Añadir los resultados encontrados a la cola
                for track in resultados:
                    track['requester'] = interaction.user.display_name
                    queue.append(track)
                
                # Feedback visual según la cantidad de temas
                if len(resultados) > 1:
                    msg = await interaction.followup.send(f"✅ **Colección:** Se añadieron `{len(resultados)}` canciones de la lista.")
                else:
                    titulo = resultados[0].get('title', 'Canción')
                    msg = await interaction.followup.send(f"✅ **En cola:** {titulo}")
                
                await msg.delete(delay=20)

            # --- INICIO DEL REPRODUCTOR ---
            vc = interaction.guild.voice_client
            # Si el bot está libre, empezamos a sonar de inmediato
            if not vc.is_playing() and not vc.is_paused():
                self.manager.play_next(interaction)

        except Exception as e:
            print(f"❌ Error crítico en comando Play: {e}")
            msg = await interaction.followup.send(f"❌ Hubo un error procesando la solicitud: {e}", ephemeral=True)
            await msg.delete(delay=20)

    # --- SISTEMA DE AUTOCOMPLETADO ---
    @play.autocomplete('buscar')
    async def buscar_autocomplete(self, interaction: discord.Interaction, current: str):
        """Ofrece sugerencias de búsqueda de YouTube en tiempo real."""
        if not current or len(current) < 3: 
            return []
            
        # Si parece un link, no sugerimos nada extra
        if current.startswith(('http', 'www')):
            return [app_commands.Choice(name="🔗 Enlace directo detectado", value=current)]
            
        try:
            # Consultamos la API de sugerencias de Google/YouTube
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={current}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        raw_data = await response.text()
                        suggestions = re.findall(r'\["([^"]+)"', raw_data)
                        # Retornamos las primeras 10 sugerencias
                        return [app_commands.Choice(name=s[:100], value=s) for s in suggestions[1:11]]
        except Exception: 
            return []
        return []

# Función obligatoria para que el bot cargue este archivo como un Cog
async def setup(bot):
    await bot.add_cog(Play(bot))