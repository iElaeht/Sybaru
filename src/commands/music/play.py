import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
from src.utils.database import get_playlist

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Reproduce música o carga tu playlist (si no escribes nada, carga tu lista)")
    @app_commands.describe(
        buscar="Escribe el nombre de la canción o pega el link",
        playlist="Marca True para cargar tu playlist personal"
    )
    async def play(self, interaction: discord.Interaction, buscar: str = None, playlist: bool = False):
        # 1. Verificación de voz (Indispensable)
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ ¡Entra a un canal de voz primero!", ephemeral=True)

        manager = self.bot.get_cog('MusicManager')
        if not manager:
            return await interaction.response.send_message("❌ Error: MusicManager no encontrado.")

        # --- LÓGICA DE ASUNCIÓN AUTOMÁTICA ---
        # Si no escribió nada Y no marcó playlist=True, forzamos playlist=True
        if buscar is None and playlist is False:
            playlist = True

        # --- EJECUCIÓN DE PLAYLIST ---
        if playlist:
            await interaction.response.defer()
            songs = get_playlist(interaction.user.id)
            
            if not songs:
                return await interaction.followup.send("❌ Tu playlist personal está vacía. ¡Usa el botón ⭐ para guardar música!")

            queue = manager.get_queue(interaction.guild.id)
            for title, url in songs:
                queue.append({
                    'title': title,
                    'url': url,
                    'thumbnail': None,
                    'user': interaction.user
                })
            
            await interaction.followup.send(f"📂 Cargando **{len(songs)}** canciones de tu colección personal...")
            
            # Conexión al canal de voz si no está dentro
            vc = interaction.guild.voice_client
            if not vc:
                vc = await interaction.user.voice.channel.connect()
            
            # Reproducir si está en silencio
            if not vc.is_playing():
                ctx = await self.bot.get_context(interaction)
                manager.play_next(ctx)
            return

        # --- LÓGICA DE BÚSQUEDA NORMAL ---
        # Si llegó aquí es porque 'buscar' tiene contenido
        await manager.process_play(interaction, buscar)

    @play.autocomplete('buscar')
    async def play_autocomplete(self, interaction: discord.Interaction, current: str):
        if not current or len(current) < 3 or current.startswith('http'): return []
        opts = {'format': 'bestaudio', 'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch5:{current}", download=False)
                return [app_commands.Choice(name=e['title'][:95], value=e['url']) for e in info['entries']]
            except: return []

    # --- COMANDOS DE CONTROL (SKIP, STOP, QUEUE, LOOP) ---
    @app_commands.command(name="skip", description="Salta la canción actual")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭️ Canción saltada.")
        else:
            await interaction.response.send_message("❌ No hay nada sonando.", ephemeral=True)

    @app_commands.command(name="stop", description="Detiene la música y limpia la cola")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        manager = self.bot.get_cog('MusicManager')
        if vc:
            if manager:
                manager.get_queue(interaction.guild.id).clear()
                if interaction.guild.id in manager.loops: manager.loops[interaction.guild.id] = False
            await vc.disconnect()
            await interaction.response.send_message("👋 ¡Adiós! Música detenida y cola limpia.")
        else:
            await interaction.response.send_message("❌ No estoy conectado.", ephemeral=True)

    @app_commands.command(name="queue", description="Muestra las próximas canciones")
    async def queue(self, interaction: discord.Interaction):
        manager = self.bot.get_cog('MusicManager')
        if manager:
            queue = manager.get_queue(interaction.guild.id)
            if not queue:
                return await interaction.response.send_message("La cola está vacía.", ephemeral=True)
            fmt = "\n".join([f"**{i+1}.** {song['title']}" for i, song in enumerate(list(queue)[:10])])
            embed = discord.Embed(title="📜 Cola de Sybaru", description=fmt, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Activa o desactiva la repetición")
    async def loop(self, interaction: discord.Interaction):
        manager = self.bot.get_cog('MusicManager')
        if manager:
            status = manager.toggle_loop(interaction.guild.id)
            await interaction.response.send_message(f"🔁 Repetición {'**activada**' if status else '**desactivada**'}.")

async def setup(bot):
    await bot.add_cog(Play(bot))