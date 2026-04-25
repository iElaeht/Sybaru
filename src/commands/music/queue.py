import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Aseguramos el acceso al MusicManager centralizado
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="queue", 
        description="Muestra la lista de canciones que sonarán a continuación"
    )
    async def queue(self, interaction: discord.Interaction):
        """Muestra el estado actual de la reproducción y la lista de espera."""
        
        guild_id = interaction.guild_id
        queue = self.manager.get_queue(guild_id)
        current = self.manager.current_track.get(guild_id)

        # Si no hay nada sonando ni en espera
        if not current and len(queue) == 0:
            return await interaction.response.send_message(
                "📭 La cola está vacía ahora mismo.", 
                ephemeral=True
            )

        # Creación del diseño del Embed
        embed = discord.Embed(
            title=f"🎶 Cola de reproducción - {interaction.guild.name}",
            color=discord.Color.blurple()
        )

        # 1. Bloque "Sonando ahora"
        if current:
            # Manejo seguro del solicitante (requester)
            requester = current.get('requester', 'Sistema')
            embed.add_field(
                name="▶️ Sonando ahora",
                value=f"[{current['title']}]({current['webpage_url']})\n`Pedido por: {requester}`",
                inline=False
            )

        # 2. Bloque "Próximas canciones" (Máximo 10 para legibilidad)
        if len(queue) > 0:
            lista_texto = ""
            # Convertimos a lista para poder usar slicing [:10]
            for i, cancion in enumerate(list(queue)[:10], start=1):
                # Manejo seguro de títulos y requesters en la cola
                titulo = cancion.get('title', 'Canción desconocida')
                url = cancion.get('webpage_url', '#')
                user = cancion.get('requester', 'Desconocido')
                
                lista_texto += f"`{i}.` [{titulo}]({url}) | `@{user}`\n"
            
            # Indicador de canciones restantes
            if len(queue) > 10:
                lista_texto += f"\n*... y {len(queue) - 10} canciones más.*"
            
            embed.add_field(name="📋 Próximas en la lista", value=lista_texto, inline=False)
        else:
            embed.add_field(name="📋 Próximas en la lista", value="No hay más canciones en espera.", inline=False)

        # 3. Estado del servidor y Loop
        loop_status = "✅ Activado" if self.manager.loop_states.get(guild_id) else "❌ Desactivado"
        total_temas = len(queue) + (1 if current else 0)
        
        embed.set_footer(text=f"Total: {total_temas} temas | 🔁 Bucle: {loop_status}")

        # Enviamos la respuesta
        await interaction.response.send_message(embed=embed)

        # 4. Limpieza: Borramos la cola después de 30 segundos para evitar confusión
        # (La cola cambia rápido, un mensaje viejo puede engañar al usuario)
        await asyncio.sleep(30)
        try:
            await interaction.delete_original_response()
        except:
            pass

async def setup(bot):
    """Carga el Cog en el sistema."""
    await bot.add_cog(Queue(bot))