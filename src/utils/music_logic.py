import discord
import yt_dlp
import asyncio
import os
from collections import deque

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'nocheckcertificate': True,
    'cookiefile': 'youtube_cookies.txt', 
    'source_address': '0.0.0.0',
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
        self.disconnect_tasks = {} 
        self.song_counters = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
            self.song_counters[guild_id] = 0
        return self.queues[guild_id]

    async def actualizar_interfaz(self, target, info):
        from src.views.music_embeds import create_now_playing_embed
        from src.views.music_buttons import MusicControlView
        
        guild_id = target.guild.id
        channel = target.channel if hasattr(target, 'channel') else self.bot.get_channel(target.channel_id)
        if not channel: return

        is_looping = self.loop_states.get(guild_id, False)
        queue = self.get_queue(guild_id)
        posicion_actual = self.song_counters.get(guild_id, 0)
        
        if posicion_actual == 0: posicion_actual = 1
        total_cola = posicion_actual + len(queue)

        if guild_id in self.current_messages:
            try: await self.current_messages[guild_id].delete()
            except: pass 

        try:
            embed = create_now_playing_embed(
                info, 
                loop_active=is_looping, 
                current_pos=posicion_actual, 
                total_queue=total_cola
            )
            view = MusicControlView(self.bot)
            msg = await channel.send(embed=embed, view=view)
            self.current_messages[guild_id] = msg
        except Exception as e:
            print(f"Error al enviar interfaz: {e}")

    def play_next(self, target):
        guild_id = target.guild.id
        vc = target.guild.voice_client
        if not vc or not vc.is_connected(): return

        if guild_id in self.disconnect_tasks:
            self.disconnect_tasks[guild_id].cancel()
            self.disconnect_tasks.pop(guild_id, None)

        queue = self.get_queue(guild_id)
        is_loop = self.loop_states.get(guild_id, False)
        
        if is_loop and self.current_track.get(guild_id):
            queue.appendleft(self.current_track[guild_id])
        else:
            self.song_counters[guild_id] = self.song_counters.get(guild_id, 0) + 1

        if len(queue) > 0:
            proxima = queue.popleft()
            self.current_track[guild_id] = proxima
            
            async def start_playing():
                try:
                    loop = asyncio.get_event_loop()
                    # Usamos process=True para obtener la URL directa final
                    data = await loop.run_in_executor(
                        None, 
                        lambda: ytdl.extract_info(proxima['webpage_url'], download=False, process=True)
                    )
                    if not data: return self.play_next(target)

                    source_url = data.get('url')
                    
                    # MEJORA AQUÍ: Especificamos el ejecutable "ffmpeg" y añadimos reconexión
                    # El ejecutable="ffmpeg" es VITAL en Render/Linux
                    raw_source = discord.FFmpegPCMAudio(
                        source_url, 
                        executable="ffmpeg", 
                        **FFMPEG_OPTIONS
                    )
                    
                    # Envolvemos en un transformador de volumen para mayor estabilidad
                    source = discord.PCMVolumeTransformer(raw_source)

                    vc.play(
                        source, 
                        after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next, target)
                    )
                    
                    await self.actualizar_interfaz(target, proxima)

                except Exception as e:
                    print(f"Error crítico en MusicManager: {e}")
                    # Si falla, esperamos un poco y saltamos a la siguiente para no buclear el error
                    await asyncio.sleep(2)
                    self.play_next(target)

            self.bot.loop.create_task(start_playing())
        else:
            self.song_counters[guild_id] = 0
            self.current_track[guild_id] = None
            self.disconnect_tasks[guild_id] = self.bot.loop.create_task(self._esperar_y_desconectar(guild_id))
            self.current_messages.pop(guild_id, None)

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
        estado = not self.loop_states.get(guild_id, False)
        self.loop_states[guild_id] = estado
        return estado

    def stop(self, interaction):
        gid = interaction.guild.id
        if gid in self.disconnect_tasks:
            self.disconnect_tasks[gid].cancel()
            self.disconnect_tasks.pop(gid, None)

        if gid in self.queues: self.queues[gid].clear()
        self.song_counters[gid] = 0
        self.loop_states[gid] = False
        self.current_track[gid] = None
        
        if gid in self.current_messages:
            self.current_messages.pop(gid, None)
            
        if interaction.guild.voice_client: 
            interaction.guild.voice_client.stop()

    def skip(self, interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop() 
            return True
        return False

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
            print(f"Error en busqueda de informacion: {e}")
            return []

    def _formatear_track(self, entry):
        v_id = entry.get('id')
        thumb = entry.get('thumbnail')
        if (not thumb or "imgur" in thumb) and v_id:
            thumb = f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
        
        return {
            'webpage_url': entry.get('webpage_url') or f"https://www.youtube.com/watch?v={v_id}",
            'title': entry.get('title', 'Cancion desconocida'),
            'thumbnail': thumb or 'https://i.imgur.com/8N697X7.png',
            'duration': entry.get('duration', 0),
            'requester': None 
        }

    async def _esperar_y_desconectar(self, guild_id):
        await asyncio.sleep(300)
        guild = self.bot.get_guild(guild_id)
        if guild and guild.voice_client:
            if not guild.voice_client.is_playing() and not guild.voice_client.is_paused():
                await guild.voice_client.disconnect()