import discord
from discord.ext import commands
from discord import app_commands
from src.utils.database import get_playlist, clear_playlist, remove_from_playlist

# --- CLASE PARA LA PAGINACIÓN ---
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
        
        fmt = "\n".join([f"**{start + i + 1}.** {title}" for i, (title, url) in enumerate(page_items)])
        
        embed = discord.Embed(
            title=f"⭐ Playlist Personal de {self.user_name}",
            description=f"Usa `/playlist_remove` seguido del número para borrar una canción.\n\n{fmt}" if fmt else "No hay canciones aquí.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Página {self.current_page + 1} de {total_pages} • Total: {len(self.data)} canciones")
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

# --- CLASE PRINCIPAL DEL COG ---
class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playlist_load", description="Carga tu playlist personal a la cola")
    async def load(self, interaction: discord.Interaction):
        await interaction.response.defer()
        songs = get_playlist(interaction.user.id)
        
        if not songs:
            return await interaction.followup.send("❌ Tu playlist está vacía. ¡Guarda canciones con el botón ⭐!")

        manager = self.bot.get_cog('MusicManager')
        if not manager:
            return await interaction.followup.send("❌ Error: No se pudo encontrar el MusicManager.")

        queue = manager.get_queue(interaction.guild.id)
        
        for title, url in songs:
            queue.append({
                'title': title,
                'url': url,
                'thumbnail': None,
                'user': interaction.user
            })
        
        await interaction.followup.send(f"📂 Se han cargado **{len(songs)}** canciones de tu playlist personal.")
        
        vc = interaction.guild.voice_client
        if vc and not vc.is_playing():
            ctx = await self.bot.get_context(interaction)
            manager.play_next(ctx)

    @app_commands.command(name="playlist_queue", description="Muestra tu lista de canciones guardadas (Modo Libro)")
    async def show_queue(self, interaction: discord.Interaction):
        songs = get_playlist(interaction.user.id)
        
        if not songs:
            return await interaction.response.send_message("❌ No tienes canciones guardadas todavía.", ephemeral=True)
        
        view = PlaylistPagination(songs, interaction.user.display_name)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)

    @app_commands.command(name="playlist_remove", description="Elimina una canción específica de tu lista por su número")
    @app_commands.describe(numero="El número de la canción que quieres borrar (míralo en /playlist_queue)")
    async def remove(self, interaction: discord.Interaction, numero: int):
        # Intentamos borrar usando la función de database.py
        success = remove_from_playlist(interaction.user.id, numero)
        
        if success:
            await interaction.response.send_message(f"✅ Canción **#{numero}** eliminada de tu playlist correctamente.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ No pude encontrar la canción **#{numero}**. Verifica el número en `/playlist_queue`.", ephemeral=True)

    @app_commands.command(name="playlist_clear", description="Borra permanentemente tu playlist personal")
    async def clear(self, interaction: discord.Interaction):
        clear_playlist(interaction.user.id)
        await interaction.response.send_message("🗑️ Tu playlist personal ha sido vaciada correctamente.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Playlist(bot))