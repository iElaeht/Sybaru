import discord
import yt_dlp
import asyncio
from collections import deque

# --- CONFIGURACIÓN DE EXTRACCIÓN ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'nocheckcertificate': True,
}

# --- CONFIGURACIÓN DE AUDIO (FFMPEG) ---
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicManager:
    """
    Cerebro central de Sybaru. 
    Gestiona la reproducción, colas, estados de bucle y sincronización de UI.
    """
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}          # {guild_id: deque()}
        self.loop_states = {}     # {guild_id: bool}
        self.current_track = {}   # {guild_id: info_dict}
        self.current_messages = {} # {guild_id: discord.Message}
        self.disconnect_tasks = {} # {guild_id: asyncio.Task}

    # --- UTILIDADES DE COLA ---

    def get_queue(self, guild_id):
        """Obtiene o crea la cola para un servidor específico."""
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    # --- GESTIÓN DE INTERFAZ (UI) ---

    async def actualizar_interfaz(self, target, info):
        """Envía el Embed de reproducción y los botones de control con estado de Loop."""
        # Importaciones locales según tu estructura MVC
        from src.views.music_embeds import create_now_playing_embed
        from src.views.music_buttons import MusicControlView
        
        guild_id = target.guild.id
        channel = target.channel if hasattr(target, 'channel') else self.bot.get_channel(target.channel_id)
        
        if not channel:
            return

        # Detectar estado del loop para este servidor
        is_looping = self.loop_states.get(guild_id, False)

        # Limpiar mensaje anterior de Sybaru
        if guild_id in self.current_messages:
            try:
                await self.current_messages[guild_id].delete()
            except:
                pass 

        try:
            # Pasamos is_looping al creador del embed
            embed = create_now_playing_embed(info, loop_active=is_looping)
            view = MusicControlView(self.bot)
            msg = await channel.send(embed=embed, view=view)
            self.current_messages[guild_id] = msg
        except Exception as e:
            print(f"❌ Error al enviar interfaz de Sybaru: {e}")

    # --- LÓGICA DE REPRODUCCIÓN CORE ---

    def play_next(self, target):
        """Maneja la transición a la siguiente canción o inicia el modo espera."""
        guild_id = target.guild.id
        vc = target.guild.voice_client
        
        if not vc or not vc.is_connected():
            return

        if guild_id in self.disconnect_tasks:
            self.disconnect_tasks[guild_id].cancel()
            self.disconnect_tasks.pop(guild_id, None)

        queue = self.get_queue(guild_id)
        
        # 🔄 Lógica de Bucle (Loop): Reinsertar canción actual si el loop está activo
        if self.loop_states.get(guild_id) and self.current_track.get(guild_id):
            queue.appendleft(self.current_track[guild_id])

        if len(queue) > 0:
            proxima = queue.popleft()
            self.current_track[guild_id] = proxima
            
            async def start_playing():
                try:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        None, 
                        lambda: ytdl.extract_info(proxima['webpage_url'], download=False, process=True)
                    )
                    
                    if not data:
                        return self.play_next(target)

                    # Actualizar miniatura a alta calidad de YouTube durante la reproducción
                    video_id = data.get('id')
                    if video_id:
                        proxima['thumbnail'] = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                    source_url = data.get('url') or (data['formats'][0]['url'] if data.get('formats') else None)

                    if not source_url:
                        return self.play_next(target)

                    source = discord.FFmpegPCMAudio(source_url, **FFMPEG_OPTIONS)
                    
                    vc.play(
                        source, 
                        after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, target)
                    )
                    
                    await self.actualizar_interfaz(target, proxima)
                    
                except Exception as e:
                    print(f"❌ Error crítico en start_playing: {e}")
                    await asyncio.sleep(2)
                    self.play_next(target)

            self.bot.loop.create_task(start_playing())
        else:
            self.current_track[guild_id] = None
            self.disconnect_tasks[guild_id] = self.bot.loop.create_task(self._esperar_y_desconectar(guild_id))
            self.current_messages.pop(guild_id, None)

    # --- CONTROLES DE ESTADO ---

    def pause(self, interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            return True
        return False

    def resume(self, interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            return True
        return False

    def toggle_loop(self, guild_id):
        """Alterna el estado del bucle."""
        estado_actual = self.loop_states.get(guild_id, False)
        self.loop_states[guild_id] = not estado_actual
        return self.loop_states[guild_id]

    def stop(self, interaction):
        gid = interaction.guild.id
        if gid in self.disconnect_tasks:
            self.disconnect_tasks[gid].cancel()
            self.disconnect_tasks.pop(gid, None)

        if gid in self.queues:
            self.queues[gid].clear()
            
        self.loop_states[gid] = False
        self.current_track[gid] = None
        self.current_messages.pop(gid, None)
        
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()

    def skip(self, interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop() 
            return True
        return False

    # --- BÚSQUEDA Y FORMATEO ---

    async def buscar_info(self, busqueda):
        loop = asyncio.get_event_loop()
        try:
            es_url = busqueda.startswith(('http', 'www'))
            query = busqueda if es_url else f"ytsearch1:{busqueda}"
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False, process=False))
            
            if not data: return []
            
            tracks = []
            if 'entries' in data:
                for entry in [e for e in data['entries'] if e][:10]:
                    tracks.append(self._formatear_track(entry))
            else:
                tracks.append(self._formatear_track(data))
            return tracks
        except Exception as e:
            print(f"❌ Error en búsqueda de Sybaru: {e}")
            return []

    def _formatear_track(self, entry):
        """Estandariza los datos y asegura una miniatura de YouTube válida."""
        v_id = entry.get('id')
        thumbnail = entry.get('thumbnail')
        
        # Limpieza de miniaturas Imgur/Nulas
        if (not thumbnail or "imgur" in thumbnail) and v_id:
            thumbnail = f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
        
        return {
            'webpage_url': entry.get('webpage_url') or f"https://www.youtube.com/watch?v={v_id}",
            'title': entry.get('title', 'Canción desconocida'),
            'thumbnail': thumbnail or 'https://i.imgur.com/8N697X7.png',
            'duration': entry.get('duration', 0),
            'requester': None 
        }

    async def _esperar_y_desconectar(self, guild_id):
        await asyncio.sleep(300)
        guild = self.bot.get_guild(guild_id)
        if guild and guild.voice_client:
            if not guild.voice_client.is_playing() and not guild.voice_client.is_paused():
                await guild.voice_client.disconnect()
                print(f"💤 Sybaru se ha desconectado de {guild.name} por inactividad.")