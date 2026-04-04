import discord

class MusicControlView(discord.ui.View):
    def __init__(self, manager, guild_id):
        super().__init__(timeout=None)
        self.manager = manager
        self.guild_id = guild_id

    @discord.ui.button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.gray)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc.is_playing():
            vc.pause()
            button.style = discord.ButtonStyle.green
        else:
            vc.resume()
            button.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop() 
            await interaction.response.send_message("⏭️ Canción saltada.", ephemeral=True)

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.gray)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        loop_status = self.manager.toggle_loop(self.guild_id)
        button.style = discord.ButtonStyle.green if loop_status else discord.ButtonStyle.gray
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"🔁 Bucle {'activado' if loop_status else 'desactivado'}.", ephemeral=True)

    @discord.ui.button(label="📜 Queue", style=discord.ButtonStyle.blurple)
    async def queue_view(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = self.manager.get_queue(self.guild_id)
        if not queue:
            return await interaction.response.send_message("La cola está vacía.", ephemeral=True)
        
        fmt = "\n".join([f"**{i+1}.** {song['title']}" for i, song in enumerate(list(queue)[:10])])
        embed = discord.Embed(title="📜 Próximas canciones", description=fmt, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            self.manager.get_queue(self.guild_id).clear()
            self.manager.loops[self.guild_id] = False
            await vc.disconnect()
            await interaction.response.send_message("👋 Reproducción finalizada.", ephemeral=True)

# --- FUNCIÓN NECESARIA PARA EL MANAGER ---
def create_music_embed(data, user):
    embed = discord.Embed(
        title="🎶 Sybaru Music",
        description=f"**[{data['title']}]({data['url']})**",
        color=discord.Color.purple()
    )
    if data.get('thumbnail'):
        embed.set_image(url=data['thumbnail'])
    embed.set_footer(text=f"Pedido por {user.display_name}", icon_url=user.display_avatar.url)
    return embed

# --- FUNCIÓN NECESARIA PARA EL CARGADOR DE COGS ---
async def setup(bot):
    # No hace nada, pero evita que el bot de error al cargar el archivo
    pass