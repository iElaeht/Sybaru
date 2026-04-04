import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDO PLAY ---
    @app_commands.command(name="play", description="Reproduce música con sugerencias inteligentes")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ ¡Entra a un canal de voz!", ephemeral=True)
            
        manager = self.bot.get_cog('MusicManager')
        if manager:
            await manager.process_play(interaction, search)
        else:
            await interaction.response.send_message("❌ Error: MusicManager no cargado.")

    @play.autocomplete('search')
    async def play_autocomplete(self, interaction: discord.Interaction, current: str):
        if not current or len(current) < 3 or current.startswith('http'): return []
        opts = {'format': 'bestaudio', 'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch5:{current}", download=False)
                return [app_commands.Choice(name=e['title'][:95], value=e['url']) for e in info['entries']]
            except: return []

    # --- COMANDO SKIP ---
    @app_commands.command(name="skip", description="Salta la canción actual")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Canción saltada.")
        else:
            await interaction.response.send_message("❌ No hay nada sonando.", ephemeral=True)

    # --- COMANDO STOP ---
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
            await interaction.response.send_message("❌ No estoy conectado a un canal de voz.", ephemeral=True)

    # --- COMANDO QUEUE ---
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

    # --- COMANDO LOOP ---
    @app_commands.command(name="loop", description="Activa o desactiva la repetición de la canción actual")
    async def loop(self, interaction: discord.Interaction):
        manager = self.bot.get_cog('MusicManager')
        if manager:
            status = manager.toggle_loop(interaction.guild.id)
            await interaction.response.send_message(f"🔁 Repetición {'**activada**' if status else '**desactivada**'}.")

async def setup(bot):
    await bot.add_cog(Play(bot))