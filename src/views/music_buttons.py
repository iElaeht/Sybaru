import discord
import math
from discord.ext import commands
from src.utils.database import save_to_playlist

# --- PAGINACIÓN DE LA COLA (Estilo Libro) ---
class QueuePagination(discord.ui.View):
    def __init__(self, queue_list, current_page=0):
        super().__init__(timeout=60)
        self.queue_list = list(queue_list)
        self.current_page = current_page
        self.items_per_page = 10
        self.total_pages = math.ceil(len(self.queue_list) / self.items_per_page)

    def create_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.queue_list[start:end]

        embed = discord.Embed(
            title="📖 Registro de la Cola - Sybaru",
            description=f"Catálogo de reproducción actual • **{len(self.queue_list)}** canciones",
            color=discord.Color.from_rgb(43, 45, 49)
        )
        
        lista_texto = ""
        for i, track in enumerate(page_items, start=start + 1):
            titulo = (track['title'][:45] + '...') if len(track['title']) > 45 else track['title']
            lista_texto += f"`{i:02d}.` **{titulo}**\n"
        
        embed.description += f"\n\n{lista_texto}"
        embed.set_thumbnail(url="https://i.postimg.cc/mk2FCD88/f408931f1a8e73a8ab555dfeb6128478.png")
        embed.set_footer(text=f"Página {self.current_page + 1} de {self.total_pages}")
        return embed

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("✨ Estás en la primera página.", ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("✨ Estás en la última página.", ephemeral=True, delete_after=5)

# --- PANEL DE CONTROL PRINCIPAL DE SYBARU ---
class MusicControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None) # Persistente
        self.bot = bot
        self.manager = bot.music_manager

    # Validación de seguridad: Bot y Usuario en el mismo canal
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("❌ **Sybaru** no está conectado.", ephemeral=True, delete_after=10)
            return False
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message("⚠️ Debes estar en el mismo canal de voz.", ephemeral=True, delete_after=10)
            return False
        return True

    # --- FILA 1: CONTROLES ---
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.blurple, row=0)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc.is_paused():
            self.manager.resume(interaction)
            await interaction.response.send_message("▶️ **Música reanudada**", ephemeral=True, delete_after=15)
        else:
            self.manager.pause(interaction)
            await interaction.response.send_message("⏸️ **Música pausada**", ephemeral=True, delete_after=15)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.gray, row=0)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.manager.skip(interaction)
        await interaction.response.send_message("⏭️ **Saltando canción...**", ephemeral=True, delete_after=15)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.gray, row=0)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        nuevo_estado = self.manager.toggle_loop(interaction.guild_id)
        button.style = discord.ButtonStyle.green if nuevo_estado else discord.ButtonStyle.gray
        # Editamos el mensaje original para que el botón cambie de color visualmente
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.red, row=0)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.manager.stop(interaction)
        await interaction.response.send_message("⏹️ **Sesión finalizada por el usuario.**", ephemeral=True, delete_after=15)

    # --- FILA 2: UTILIDADES ---
    @discord.ui.button(label="Favorito", emoji="⭐", style=discord.ButtonStyle.green, row=1)
    async def add_fav(self, interaction: discord.Interaction, button: discord.ui.Button):
        track = self.manager.current_track.get(interaction.guild_id)
        if not track:
            return await interaction.response.send_message("❌ No hay nada sonando.", ephemeral=True, delete_after=10)
        
        exito = save_to_playlist(interaction.user.id, track['title'], track['webpage_url'])
        msg = "🌟 **¡Guardada en tus favoritos!**" if exito else "⚠️ Esta canción ya estaba en tu lista."
        await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

    @discord.ui.button(label="Ver Cola", emoji="📖", style=discord.ButtonStyle.gray, row=1)
    async def show_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = self.manager.get_queue(interaction.guild_id)
        if not queue:
            return await interaction.response.send_message("📭 La cola está vacía.", ephemeral=True, delete_after=10)
        
        pagination = QueuePagination(queue)
        await interaction.response.send_message(embed=pagination.create_embed(), view=pagination, ephemeral=True)