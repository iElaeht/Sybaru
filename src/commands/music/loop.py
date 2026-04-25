import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'music_manager'):
            from src.utils.music_logic import MusicManager
            bot.music_manager = MusicManager(bot)
        self.manager = bot.music_manager

    @app_commands.command(
        name="loop", 
        description="Activa o desactiva la repetición infinita de la canción actual"
    )
    async def loop(self, interaction: discord.Interaction):
        """Alterna el estado de bucle para el servidor actual en Sybaru."""
        
        # 1. Validación de conexión
        vc = interaction.guild.voice_client
        if not vc:
            return await interaction.response.send_message(
                "❌ **Sybaru** no está conectado a un canal de voz.", 
                ephemeral=True
            )

        # 2. Seguridad de canal
        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            return await interaction.response.send_message(
                "⚠️ Debes estar en el mismo canal que **Sybaru**.", 
                ephemeral=True
            )

        # 3. Cambio de estado (Aseguramos que sea rápido)
        try:
            guild_id = interaction.guild_id
            nuevo_estado = self.manager.toggle_loop(guild_id)

            # 4. Creación del Embed
            if nuevo_estado:
                embed = discord.Embed(
                    title="🔁 Bucle Activado",
                    description="La canción actual se repetirá indefinidamente.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="➡️ Bucle Desactivado",
                    description="La reproducción seguirá el orden de la cola.",
                    color=discord.Color.light_grey()
                )
            
            embed.set_footer(text="Sybaru Music System")

            # 5. Respuesta
            # Usamos ephemeral=True si quieres evitar que el bot borre mensajes manualmente
            # Pero si prefieres que todos lo vean, mantenemos el borrado:
            await interaction.response.send_message(embed=embed)

            # 6. Borrado seguro
            await asyncio.sleep(10)
            try:
                await interaction.delete_original_response()
            except discord.NotFound:
                pass # El mensaje ya fue borrado por un usuario
            except Exception as e:
                print(f"Error al borrar mensaje de loop: {e}")

        except Exception as e:
            print(f"❌ Error en el comando loop: {e}")
            # Si el manager falló, intentamos avisar al usuario
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Error al cambiar el estado del bucle.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Loop(bot))