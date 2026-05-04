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
        if not hasattr(bot, 'music_manager'):
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="play", 
        description="Reproduce musica de YouTube o tus favoritos"
    )
    @app_commands.describe(
        buscar="Nombre de la cancion o link de YouTube",
        playlist="Carga tu lista de favoritos"
    )
    @app_commands.choices(playlist=[
        app_commands.Choice(name="Cargar mis Favoritos", value="yes")
    ])
    async def play(
        self, 
        interaction: discord.Interaction, 
        buscar: str = None, 
        playlist: app_commands.Choice[str] = None
    ):
        await interaction.response.defer()

        if not interaction.user.voice:
            msg = await interaction.followup.send("Debes estar en un canal de voz", ephemeral=True)
            await msg.delete(delay=10)
            return

        if not playlist and not buscar:
            msg = await interaction.followup.send("Especifica una cancion o elige tus favoritos", ephemeral=True)
            await msg.delete(delay=10)
            return

        if not interaction.guild.voice_client:
            try:
                await interaction.user.voice.channel.connect()
            except Exception as e:
                msg = await interaction.followup.send(f"Error al unir al canal: {e}", ephemeral=True)
                await msg.delete(delay=10)
                return

        try:
            queue = self.manager.get_queue(interaction.guild_id)
            vc = interaction.guild.voice_client
            COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)

            if playlist and playlist.value == "yes":
                canciones_db = get_playlist(interaction.user.id)
                if not canciones_db:
                    msg = await interaction.followup.send("No hay canciones en tu lista", ephemeral=True)
                    await msg.delete(delay=10)
                    return
                
                for titulo, url in canciones_db:
                    queue.append({
                        'title': titulo, 
                        'webpage_url': url, 
                        'url': None, 
                        'requester': interaction.user.display_name, 
                        'thumbnail': None
                    })
                
                embed = discord.Embed(title="Coleccion Personal Cargada", color=COLOR_SYBARU)
                embed.description = f"Se han añadido {len(canciones_db)} temas a la lista."
                msg = await interaction.followup.send(embed=embed)
                await msg.delete(delay=15)

            elif buscar:
                resultados = await self.manager.buscar_info(buscar)
                
                if not resultados:
                    msg = await interaction.followup.send(f"Sin resultados para: {buscar}", ephemeral=True)
                    await msg.delete(delay=10)
                    return

                for track in resultados:
                    track['requester'] = interaction.user.display_name
                    queue.append(track)
                
                total = len(queue)
                embed = discord.Embed(color=COLOR_SYBARU)
                
                if len(resultados) > 1:
                    embed.title = "Lista de reproduccion añadida"
                    embed.description = f"Se han sumado {len(resultados)} canciones."
                elif vc.is_playing() or vc.is_paused():
                    track = resultados[0]
                    embed.title = "Añadido a la cola"
                    embed.description = f"[{track.get('title')}]({track.get('webpage_url')})"
                    embed.set_footer(text=f"Posicion: {total}")
                else:
                    track = resultados[0]
                    embed.title = "Reproduciendo"
                    embed.description = f"[{track.get('title')}]({track.get('webpage_url')})"

                msg = await interaction.followup.send(embed=embed)
                await msg.delete(delay=15)

            if not vc.is_playing() and not vc.is_paused():
                self.manager.play_next(interaction)

        except Exception as e:
            print(f"Error en Play: {e}")
            msg = await interaction.followup.send("Error al procesar la musica", ephemeral=True)
            await msg.delete(delay=10)

    @play.autocomplete('buscar')
    async def buscar_autocomplete(self, interaction: discord.Interaction, current: str):
        if not current or len(current) < 3: 
            return []
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