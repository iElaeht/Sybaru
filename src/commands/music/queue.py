import discord
import asyncio
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
        description="Muestra la lista de canciones que sonaran a continuacion"
    )
    async def queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        queue = self.manager.get_queue(guild_id)
        current = self.manager.current_track.get(guild_id)
        COLOR_SYBARU = discord.Color.from_rgb(43, 45, 49)

        if not current and len(queue) == 0:
            msg = await interaction.response.send_message(
                "La cola esta vacia ahora mismo", 
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Cola de reproduccion - {interaction.guild.name}",
            color=COLOR_SYBARU
        )

        if current:
            requester = current.get('requester', 'Sistema')
            embed.add_field(
                name="Sonando ahora",
                value=f"[{current['title']}]({current['webpage_url']})\nPedido por: {requester}",
                inline=False
            )

        if len(queue) > 0:
            lista_texto = ""
            for i, cancion in enumerate(list(queue)[:10], start=1):
                titulo = cancion.get('title', 'Cancion desconocida')
                url = cancion.get('webpage_url', '#')
                user = cancion.get('requester', 'Desconocido')
                lista_texto += f"`{i}.` [{titulo}]({url}) | `@{user}`\n"
            
            if len(queue) > 10:
                lista_texto += f"\n... y {len(queue) - 10} canciones mas"
            
            embed.add_field(name="Proximas en la lista", value=lista_texto, inline=False)
        else:
            embed.add_field(name="Proximas en la lista", value="No hay mas canciones en espera", inline=False)

        loop_status = "Activado" if self.manager.loop_states.get(guild_id) else "Desactivado"
        total_temas = len(queue) + (1 if current else 0)
        embed.set_footer(text=f"Total: {total_temas} temas | Bucle: {loop_status}")

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(30)
        try:
            await interaction.delete_original_response()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Queue(bot))