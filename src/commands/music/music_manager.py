import discord
from discord.ext import commands
import yt_dlp
from collections import deque
from .views import MusicControlView, create_music_embed

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

class MusicManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}     # {guild_id: deque()}
        self.loops = {}      # {guild_id: bool}
        self.now_playing = {} # {guild_id: data_dict}
        self.last_messages = {} # {guild_id: message_object}

    def get_queue(self, guild_id):
        if guild_id not in self.queues: 
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    def toggle_loop(self, guild_id):
        """Activa/Desactiva el bucle y devuelve el nuevo estado."""
        current = self.loops.get(guild_id, False)
        self.loops[guild_id] = not current
        return self.loops[guild_id]

    async def cleanup_last_message(self, guild_id):
        """Deshabilita los botones del mensaje anterior para evitar bugs de interacción."""
        msg = self.last_messages.get(guild_id)
        if msg:
            try:
                # Intentamos quitar la view (botones) del mensaje anterior
                await msg.edit(view=None)
            except Exception:
                pass # Si el mensaje fue borrado o no se puede editar, ignoramos

    def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return

        # Lógica de Selección de Canción (Loop vs Queue)
        if self.loops.get(guild_id, False) and guild_id in self.now_playing:
            next_song = self.now_playing[guild_id]
        elif len(queue) > 0:
            next_song = queue.popleft()
            self.now_playing[guild_id] = next_song
        else:
            self.now_playing.pop(guild_id, None)
            # Si no hay más música, limpiamos los últimos botones y salimos
            self.bot.loop.create_task(self.cleanup_last_message(guild_id))
            return

        # Preparación del Audio
        try:
            source = discord.FFmpegOpusAudio(next_song['url'], **FFMPEG_OPTIONS)
            
            # Limpiamos botones del mensaje previo antes de enviar el nuevo
            self.bot.loop.create_task(self.cleanup_last_message(guild_id))

            def after_playing(error):
                if error: print(f'Error en reproductor: {error}')
                # Llamada recursiva para la siguiente canción
                self.play_next(ctx)

            vc.play(source, after=after_playing)
            
            # Tarea asíncrona para enviar el Embed con Controles
            async def send_status():
                embed = create_music_embed(next_song, next_song['user'])
                view = MusicControlView(self, guild_id)
                msg = await ctx.send(embed=embed, view=view)
                self.last_messages[guild_id] = msg

            self.bot.loop.create_task(send_status())
            
        except Exception as e:
            print(f"Error al reproducir audio: {e}")

    async def process_play(self, interaction, search):
        """Lógica principal para buscar y añadir música."""
        if not interaction.response.is_done(): 
            await interaction.response.defer()
        
        ctx = await self.bot.get_context(interaction)
        vc = ctx.voice_client
        
        # Conexión automática
        if not vc:
            if interaction.user.voice:
                vc = await interaction.user.voice.channel.connect()
            else:
                return await interaction.followup.send("❌ ¡Debes estar en un canal de voz!")

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Búsqueda en YouTube o carga de URL
                info = ydl.extract_info(search if search.startswith('http') else f"ytsearch:{search}", download=False)
                if 'entries' in info: info = info['entries'][0]
                
                data = {
                    'url': info['url'], 
                    'title': info['title'], 
                    'thumbnail': info.get('thumbnail'), 
                    'user': interaction.user
                }
            except Exception as e:
                return await interaction.followup.send(f"❌ Error al extraer info: {e}")

        queue = self.get_queue(interaction.guild.id)
        
        if vc.is_playing() or vc.is_paused():
            queue.append(data)
            await interaction.followup.send(f"✅ Añadido a la cola: **{data['title']}**")
        else:
            self.now_playing[interaction.guild.id] = data
            # Limpieza preventiva
            await self.cleanup_last_message(interaction.guild.id)
            
            source = discord.FFmpegOpusAudio(data['url'], **FFMPEG_OPTIONS)
            vc.play(source, after=lambda e: self.play_next(ctx))
            
            embed = create_music_embed(data, interaction.user)
            view = MusicControlView(self, interaction.guild.id)
            
            # Enviamos y guardamos el mensaje inicial
            msg = await interaction.followup.send(embed=embed, view=view)
            self.last_messages[interaction.guild.id] = msg

async def setup(bot):
    await bot.add_cog(MusicManager(bot))