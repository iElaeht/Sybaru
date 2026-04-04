import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Configuración de yt-dlp para extraer solo el audio
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Configuración de FFmpeg para la reproducción
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

class MusicManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="play", description="Reproduce música de YouTube")
    async def play(self, ctx, *, search: str):
        await ctx.defer() # Esto le da tiempo al bot para procesar el audio

        # 1. Verificar si el usuario está en un canal de voz
        if not ctx.author.voice:
            return await ctx.send("❌ ¡Debes estar en un canal de voz!")

        # 2. Conectarse al canal de voz
        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()

        # 3. Extraer la info de la canción
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                url = info['url']
                title = info['title']
            except Exception as e:
                return await ctx.send(f"❌ Error al buscar la canción: {e}")

        # 4. Reproducir el audio
        # Usamos FFmpegPCMAudio para procesar el stream
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        
        if vc.is_playing():
            vc.stop() # Por ahora, detiene la anterior para poner la nueva

        vc.play(source)
        await ctx.send(f"🎶 Reproduciendo ahora: **{title}**")

    @commands.hybrid_command(name="stop", description="Detiene la música y saca al bot")
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 ¡Desconectado!")
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

async def setup(bot):
    await bot.add_cog(MusicManager(bot))