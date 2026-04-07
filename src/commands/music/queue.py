import discord
from discord.ext import commands
from discord import app_commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="queue", 
        description="Muestra la lista de canciones en espera"
    )
    async def queue(self, interaction: discord.Interaction):
        """Muestra la cola de reproducción actual del servidor."""
        guild_id = interaction.guild_id
        queue = self.manager.get_queue(guild_id)
        current = self.manager.current_track.get(guild_id)

        if not current and len(queue) == 0:
            return await interaction.response.send_message(
                "📭 La cola está vacía ahora mismo.", 
                ephemeral=True
            )

        # Construcción del mensaje (Embed)
        embed = discord.Embed(
            title=f"🎶 Cola de reproducción - {interaction.guild.name}",
            color=discord.Color.blurple()
        )

        # 1. Mostrar qué suena ahora
        if current:
            embed.add_field(
                name="▶️ Sonando ahora",
                value=f"[{current['title']}]({current['webpage_url']}) | `Pedida por: {current['requester']}`",
                inline=False
            )

        # 2. Listar las siguientes canciones (limitamos a las primeras 10 para no saturar)
        if len(queue) > 0:
            lista_texto = ""
            for i, cancion in enumerate(list(queue)[:10], start=1):
                lista_texto += f"`{i}.` [{cancion['title']}]({cancion['webpage_url']}) | `@{cancion['requester']}`\n"
            
            if len(queue) > 10:
                lista_texto += f"\n*... y {len(queue) - 10} canciones más.*"
            
            embed.add_field(name="📋 Próximas en la lista", value=lista_texto, inline=False)
        else:
            embed.add_field(name="📋 Próximas en la lista", value="No hay más canciones en espera.", inline=False)

        # 3. Mostrar estado del Loop
        loop_status = "✅ Activado" if self.manager.loop_states.get(guild_id) else "❌ Desactivado"
        embed.set_footer(text=f"Total de canciones: {len(queue) + (1 if current else 0)} | 🔁 Bucle: {loop_status}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Queue(bot))