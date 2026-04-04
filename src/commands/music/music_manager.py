import discord
from discord.ext import commands
import yt_dlp
from collections import deque
from .views import MusicControlView, create_music_embed

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class MusicManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.loops = {}
        self.now_playing = {}
        self.last_messages = {} # <-- NUEVO: Para limpiar botones viejos

    def get_queue(self, guild_id):
        if guild_id not in self.queues: 
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    def toggle_loop(self, guild_id):
        current = self.loops.get(guild_id, False)
        self.loops[guild_id] = not current
        return self.loops[guild_id]

    async def cleanup_last_message(self, guild_id):
        """Deshabilita los botones del mensaje anterior para evitar bugs."""
        msg = self.last_messages.get(guild_id)
        if msg:
            try:
                await msg.edit(view=None) # Quitamos los botones
            except:
                pass

    def play_next(self, ctx):
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return

        if self.loops.get(guild_id, False) and guild_id in self.now_playing:
            next_song = self.now_playing[guild_id]
        elif len(queue) > 0:
            next_song = queue.popleft()
            self.now_playing[guild_id] = next_song
        else:
            self.now_playing.pop(guild_id, None)
            # Limpiamos los botones al terminar la lista
            self.bot.loop.create_task(self.cleanup_last_message(guild_id))
            return

        source = discord.FFmpegOpusAudio(next_song['url'], **FFMPEG_OPTIONS)
        
        # Limpiamos botones anteriores antes de poner la nueva canción
        self.bot.loop.create_task(self.cleanup_last_message(guild_id))

        def after_playing(error):
            if error: print(f'Error en reproductor: {error}')
            self.play_next(ctx)

        vc.play(source, after=after_playing)
        
        # Usamos una tarea para enviar el mensaje y GUARDARLO
        async def send_status():
            embed = create_music_embed(next_song, next_song['user'])
            # IMPORTANTE: Pasamos 'self' para que la View tenga el manager
            view = MusicControlView(self, guild_id)
            msg = await ctx.send(embed=embed, view=view)
            self.last_messages[guild_id] = msg

        self.bot.loop.create_task(send_status())

    async def process_play(self, interaction, search):
        if not interaction.response.is_done(): 
            await interaction.response.defer()
        
        ctx = await self.bot.get_context(interaction)
        vc = ctx.voice_client
        
        if not vc:
            if interaction.user.voice:
                vc = await interaction.user.voice.channel.connect()
            else:
                return await interaction.followup.send("❌ ¡Entra a un canal de voz!")

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search if search.startswith('http') else f"ytsearch:{search}", download=False)
                if 'entries' in info: info = info['entries'][0]
                data = {'url': info['url'], 'title': info['title'], 'thumbnail': info.get('thumbnail'), 'user': interaction.user}
            except Exception as e:
                return await interaction.followup.send(f"❌ Error: {e}")

        queue = self.get_queue(interaction.guild.id)
        
        if vc.is_playing() or vc.is_paused():
            queue.append(data)
            await interaction.followup.send(f"✅ En cola: **{data['title']}**")
        else:
            self.now_playing[interaction.guild.id] = data
            # Limpiar botones si había un mensaje de una sesión anterior
            await self.cleanup_last_message(interaction.guild.id)
            
            source = discord.FFmpegOpusAudio(data['url'], **FFMPEG_OPTIONS)
            vc.play(source, after=lambda e: self.play_next(ctx))
            
            embed = create_music_embed(data, interaction.user)
            view = MusicControlView(self, interaction.guild.id)
            msg = await interaction.followup.send(embed=embed, view=view)
            
            # Guardamos este mensaje como el último
            if isinstance(msg, discord.WebhookMessage):
                self.last_messages[interaction.guild.id] = msg
            else:
                self.last_messages[interaction.guild.id] = msg

async def setup(bot):
    await bot.add_cog(MusicManager(bot))