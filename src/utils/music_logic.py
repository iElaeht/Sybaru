import yt_dlp
import discord
import asyncio
from collections import deque

# Configuración de extracción optimizada
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist', 
    'noplaylist': False,            
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicManager:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.loop_states = {}
        self.current_track = {}
        self.current_messages = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def actualizar_interfaz(self, target, info):
        """Maneja la salida visual: Borra lo anterior y envía el nuevo Embed con botones."""
        from src.views.music_embeds import create_now_playing_embed
        from src.views.music_buttons import MusicControlView
        
        guild_id = target.guild.id
        
        # Obtener el canal de forma segura
        channel = target.channel if hasattr(target, 'channel') else self.bot.get_channel(target.channel_id)
        if not channel: return

        # 1. ELIMINAR MENSAJE PREVIO (Evita botones huérfanos)
        if guild_id in self.current_messages:
            try:
                await self.current_messages[guild_id].delete()
            except:
                pass 

        # 2. ENVIAR NUEVA INTERFAZ
        try:
            embed = create_now_playing_embed(info)
            view = MusicControlView(self.bot)
            msg = await channel.send(embed=embed, view=view)
            self.current_messages[guild_id] = msg
        except Exception as e:
            print(f"Error al enviar interfaz: {e}")

    def play_next(self, target):
        """Lógica de reproducción en cadena."""
        guild_id = target.guild.id
        voice_client = target.guild.voice_client
        
        if not voice_client or not voice_client.is_connected():
            return

        queue = self.get_queue(guild_id)
        
        if self.loop_states.get(guild_id) and self.current_track.get(guild_id):
            queue.appendleft(self.current_track[guild_id])

        if len(queue) > 0:
            proxima = queue.popleft()
            self.current_track[guild_id] = proxima
            
            async def start_playing():
                try:
                    loop = asyncio.get_event_loop()
                    
                    # Extraer URL real de stream (esto actualiza info necesaria para el embed)
                    data = await loop.run_in_executor(
                        None, 
                        lambda: ytdl.extract_info(proxima['webpage_url'], download=False, process=True)
                    )
                    
                    if not data:
                        return self.play_next(target)

                    # Actualizamos el diccionario con datos frescos para el Embed
                    proxima['title'] = data.get('title', proxima['title'])
                    proxima['thumbnail'] = data.get('thumbnail', proxima['thumbnail'])
                    proxima['duration'] = data.get('duration', proxima['duration'])

                    source_url = data.get('url')
                    if not source_url and data.get('formats'):
                        source_url = data['formats'][0]['url']

                    if not source_url:
                        return self.play_next(target)

                    source = discord.FFmpegPCMAudio(source_url, **FFMPEG_OPTIONS)
                    
                    # Al terminar la canción, se llama a sí mismo
                    voice_client.play(
                        source, 
                        after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, target)
                    )
                    
                    # --- SALIDA VISUAL ---
                    await self.actualizar_interfaz(target, proxima)
                    
                except Exception as e:
                    print(f"Error en play_next: {e}")
                    await asyncio.sleep(2)
                    self.play_next(target)

            self.bot.loop.create_task(start_playing())
        else:
            self.current_track[guild_id] = None
            # Si la cola termina, limpiamos la referencia del mensaje
            if guild_id in self.current_messages:
                self.current_messages.pop(guild_id)

    # --- LÓGICA DE CONTROL ---

    def toggle_loop(self, guild_id):
        """Cambia el estado del bucle (necesario para el botón 🔁)."""
        estado = not self.loop_states.get(guild_id, False)
        self.loop_states[guild_id] = estado
        return estado

    # (Funciones buscar_info y _formatear_track se mantienen igual por tu petición)
    async def buscar_info(self, busqueda):
        loop = asyncio.get_event_loop()
        try:
            es_url = busqueda.startswith(('http', 'www'))
            query = busqueda if es_url else f"ytsearch1:{busqueda}"
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False, process=False))
            if not data: return []
            tracks_encontrados = []
            if 'entries' in data:
                entries = [e for e in data['entries'] if e]
                if not es_url or 'ytsearch' in data.get('extractor', ''):
                    if entries: tracks_encontrados.append(self._formatear_track(entries[0]))
                else:
                    for entry in entries[:10]: tracks_encontrados.append(self._formatear_track(entry))
            else:
                tracks_encontrados.append(self._formatear_track(data))
            return tracks_encontrados
        except Exception as e:
            print(f"Error en buscar_info: {e}")
            return []

    def _formatear_track(self, entry):
        video_id = entry.get('id')
        web_url = entry.get('webpage_url') or (f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url'))
        return {
            'webpage_url': web_url,
            'title': entry.get('title') or 'Canción desconocida',
            'thumbnail': entry.get('thumbnail') or 'https://i.imgur.com/8N697X7.png',
            'duration': entry.get('duration') or 0,
            'url': entry.get('url'), 
            'requester': None
        }

    def pause(self, t):
        vc = t.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            return True
        return False

    def resume(self, t):
        vc = t.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            return True
        return False

    def skip(self, t):
        vc = t.guild.voice_client
        if vc:
            vc.stop()
            return True
        return False

    def stop(self, t):
        gid = t.guild.id
        if gid in self.queues: self.queues[gid].clear()
        self.loop_states[gid] = False
        if gid in self.current_messages:
            self.current_messages.pop(gid)
        if t.guild.voice_client:
            t.guild.voice_client.stop()