import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from src.utils.database import get_playlist, clear_full_playlist, remove_from_playlist, save_to_playlist

class PlaylistPagination(discord.ui.View):
    def __init__(self, data, user_name):
        super().__init__(timeout=60)
        self.data = data
        self.user_name = user_name
        self.current_page = 0
        self.items_per_page = 10 
        self.total_pages = (len(self.data) - 1) // self.items_per_page + 1

    def create_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.data[start:end]
        
        fmt = "\n".join([f"**{start + i + 1}.** {title}" for i, (title, url) in enumerate(page_items)])
        
        embed = discord.Embed(
            title=f"Favoritos de {self.user_name}",
            description=f"{fmt}" if fmt else "La lista esta vacia",
            color=discord.Color.from_rgb(43, 45, 49)
        )
        embed.set_footer(text=f"Pagina {self.current_page + 1} de {self.total_pages} - {len(self.data)} temas")
        return embed

    def update_buttons(self):
        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page >= self.total_pages - 1)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = getattr(bot, 'music_manager', None)

    @app_commands.command(name="playlist_add", description="Guarda una cancion en tus favoritos")
    @app_commands.describe(busqueda="Nombre o URL de la cancion")
    async def add(self, interaction: discord.Interaction, busqueda: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            resultados = await self.bot.music_manager.buscar_info(busqueda)
            if not resultados:
                msg = await interaction.followup.send("No se encontro la cancion")
                await asyncio.sleep(10)
                return await msg.delete()

            track = resultados[0]
            exito = save_to_playlist(interaction.user.id, track['title'], track['webpage_url'])
            
            if exito:
                msg = await interaction.followup.send(f"Guardada en favoritos: {track['title']}")
            else:
                msg = await interaction.followup.send("La cancion ya existe en tu lista")
            
            await asyncio.sleep(10)
            await msg.delete()
                
        except Exception as e:
            msg = await interaction.followup.send(f"Error al guardar: {e}")
            await asyncio.sleep(10)
            await msg.delete()

    @app_commands.command(name="playlist_queue", description="Muestra tu lista de favoritos")
    async def show_queue(self, interaction: discord.Interaction):
        songs = get_playlist(interaction.user.id)
        if not songs:
            msg = await interaction.response.send_message("Tu lista de favoritos esta vacia", ephemeral=True)
            await asyncio.sleep(10)
            return await interaction.delete_original_response()
        
        view = PlaylistPagination(songs, interaction.user.display_name)
        view.update_buttons()
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)

    @app_commands.command(name="playlist_remove", description="Elimina una cancion por su posicion")
    @app_commands.describe(numero="Numero de la cancion en la lista")
    async def remove(self, interaction: discord.Interaction, numero: int):
        songs = get_playlist(interaction.user.id)
        
        if numero <= 0 or numero > len(songs):
            msg = await interaction.response.send_message(f"Numero invalido. Tienes {len(songs)} canciones", ephemeral=True)
            await asyncio.sleep(10)
            return await interaction.delete_original_response()

        _, song_url = songs[numero - 1]
        
        if remove_from_playlist(interaction.user.id, song_url):
            await interaction.response.send_message(f"Cancion {numero} eliminada de favoritos", ephemeral=True)
        else:
            await interaction.response.send_message("No se pudo eliminar la cancion", ephemeral=True)
        
        await asyncio.sleep(10)
        await interaction.delete_original_response()

    @app_commands.command(name="playlist_clear", description="Vacia tu lista de favoritos")
    async def clear(self, interaction: discord.Interaction):
        if clear_full_playlist(interaction.user.id):
            await interaction.response.send_message("Lista de favoritos vaciada", ephemeral=True)
        else:
            await interaction.response.send_message("Error al limpiar la lista", ephemeral=True)
        
        await asyncio.sleep(10)
        await interaction.delete_original_response()

async def setup(bot):
    await bot.add_cog(Playlist(bot))