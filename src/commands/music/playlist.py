import discord
from discord.ext import commands
from discord import app_commands
# Importaciones sincronizadas con tu database.py
from src.utils.database import get_playlist, clear_playlist, remove_from_playlist, save_to_playlist

# --- VISTA PARA LA PAGINACIÓN (Modo Libro) ---
class PlaylistPagination(discord.ui.View):
    def __init__(self, data, user_name):
        super().__init__(timeout=60)
        self.data = data
        self.user_name = user_name
        self.current_page = 0
        self.items_per_page = 10 

    def create_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.data[start:end]
        total_pages = (len(self.data) - 1) // self.items_per_page + 1
        
        # Usamos los datos (song_title, song_url) que devuelve tu fetchall()
        fmt = "\n".join([f"**{start + i + 1}.** {title}" for i, (title, url) in enumerate(page_items)])
        
        embed = discord.Embed(
            title=f"⭐ Playlist Personal de {self.user_name}",
            description=f"Gestiona tus favoritos.\n\n{fmt}" if fmt else "Tu lista está vacía.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Página {self.current_page + 1} de {total_pages} • Total: {len(self.data)} temas")
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("Ya estás en la primera página.", ephemeral=True)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.current_page + 1) * self.items_per_page < len(self.data):
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("Ya estás en la última página.", ephemeral=True)

# --- COG PRINCIPAL ---
class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Aseguramos conexión al Manager
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(name="playlist_add", description="Guarda una canción en tu lista personal")
    @app_commands.describe(busqueda="Nombre o URL de la canción para guardar")
    async def add(self, interaction: discord.Interaction, busqueda: str):
        await interaction.response.defer(ephemeral=True)
        try:
            # Buscamos la info para guardar el Título y URL real
            info = await self.manager.buscar_info(busqueda)
            
            # Sincronizado con save_to_playlist de tu database.py
            exito = save_to_playlist(interaction.user.id, info['title'], info['webpage_url'])
            
            if exito:
                await interaction.followup.send(f"✅ Guardada: **{info['title']}**")
            else:
                await interaction.followup.send("⚠️ Esa canción ya está en tu playlist.")
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error al guardar: {e}")

    @app_commands.command(name="playlist_queue", description="Muestra tus favoritos (Modo Libro)")
    async def show_queue(self, interaction: discord.Interaction):
        songs = get_playlist(interaction.user.id)
        if not songs:
            return await interaction.response.send_message("❌ No tienes canciones guardadas.", ephemeral=True)
        
        view = PlaylistPagination(songs, interaction.user.display_name)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)

    @app_commands.command(name="playlist_remove", description="Borra una canción por su número")
    async def remove(self, interaction: discord.Interaction, numero: int):
        # Sincronizado con remove_from_playlist de tu database.py
        success = remove_from_playlist(interaction.user.id, numero)
        if success:
            await interaction.response.send_message(f"✅ Canción **#{numero}** eliminada.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ No encontré la canción #{numero}.", ephemeral=True)

    @app_commands.command(name="playlist_clear", description="Borra toda tu playlist")
    async def clear(self, interaction: discord.Interaction):
        # Sincronizado con clear_playlist de tu database.py
        clear_playlist(interaction.user.id)
        await interaction.response.send_message("🗑️ Tu playlist personal ha sido vaciada.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Playlist(bot))