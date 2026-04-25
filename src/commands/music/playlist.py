import discord
from discord.ext import commands
from discord import app_commands
# Importamos con los nombres EXACTOS de nuestra database.py
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
        
        # Formateo mejorado con subtítulo
        fmt = "\n".join([f"**{start + i + 1}.** {title}" for i, (title, url) in enumerate(page_items)])
        
        embed = discord.Embed(
            title=f"⭐ Favoritos de {self.user_name}",
            description=f"> *Puedes gestionar tus temas guardados y escucharlos en cualquier momento.*\n\n{fmt}" if fmt else "Tu lista está vacía.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Página {self.current_page + 1} de {self.total_pages} • {len(self.data)} temas totales")
        return embed

    def update_buttons(self):
        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page >= self.total_pages - 1)

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Asumimos que MusicManager ya está configurado en el bot
        self.manager = getattr(bot, 'music_manager', None)

    @app_commands.command(name="playlist_add", description="Guarda una canción en tus favoritos")
    @app_commands.describe(busqueda="Nombre o URL de la canción")
    async def add(self, interaction: discord.Interaction, busqueda: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Necesitamos el manager para extraer la info (Título y URL real)
            resultados = await self.bot.music_manager.buscar_info(busqueda)
            if not resultados:
                return await interaction.followup.send("❌ No encontré ninguna canción con ese nombre.", delete_after=15)

            track = resultados[0]
            exito = save_to_playlist(interaction.user.id, track['title'], track['webpage_url'])
            
            if exito:
                await interaction.followup.send(f"✅ **Guardada en favoritos:**\n`{track['title']}`", delete_after=15)
            else:
                await interaction.followup.send("⚠️ Esa canción ya existe en tu lista personal.", delete_after=15)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error al guardar: {e}", delete_after=15)

    @app_commands.command(name="playlist_queue", description="Muestra tu lista de favoritos")
    async def show_queue(self, interaction: discord.Interaction):
        songs = get_playlist(interaction.user.id)
        if not songs:
            return await interaction.response.send_message("❌ Tu lista de favoritos está vacía.", ephemeral=True)
        
        view = PlaylistPagination(songs, interaction.user.display_name)
        view.update_buttons()
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)

    @app_commands.command(name="playlist_remove", description="Elimina una canción por su posición")
    @app_commands.describe(numero="El número de la canción en tu /playlist_queue")
    async def remove(self, interaction: discord.Interaction, numero: int):
        songs = get_playlist(interaction.user.id) # Obtenemos la lista actual
        
        if numero <= 0 or numero > len(songs):
            return await interaction.response.send_message(f"❌ Número inválido. Tienes {len(songs)} canciones.", ephemeral=True, delete_after=15)

        # Obtenemos la URL de la canción en esa posición (ajustando índice 0)
        _, song_url = songs[numero - 1]
        
        if remove_from_playlist(interaction.user.id, song_url):
            await interaction.response.send_message(f"🗑️ Canción **#{numero}** eliminada de tus favoritos.", ephemeral=True, delete_after=15)
        else:
            await interaction.response.send_message("❌ No se pudo eliminar la canción.", ephemeral=True, delete_after=15)

    @app_commands.command(name="playlist_clear", description="Vacía completamente tu lista de favoritos")
    async def clear(self, interaction: discord.Interaction):
        if clear_full_playlist(interaction.user.id):
            await interaction.response.send_message("🧹 Tu playlist personal ha sido vaciada.", ephemeral=True, delete_after=15)
        else:
            await interaction.response.send_message("❌ Hubo un error al limpiar tu playlist.", ephemeral=True, delete_after=15)

async def setup(bot):
    await bot.add_cog(Playlist(bot))