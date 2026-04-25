import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import os
import re
import asyncio

class ConverTikt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_path = "src/cache"
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    # Expresión regular para detectar enlaces de TikTok en varios formatos
    TIKTOK_REGEX = r"(https?://(?:www\.|vm\.|vt\.|v\.)?tiktok\.com/[^\s]+)"

    def download_tiktok(self, url, file_path):
        """
        Configuración de descarga. 
        Usa un User-Agent moderno para evitar errores de extracción.
        """
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def process_tikt(self, ctx_or_interaction, target_message):
        """
        Lógica central: Extrae metadatos, descarga el video y limpia el chat.
        """
        is_slash = isinstance(ctx_or_interaction, discord.Interaction)
        channel = ctx_or_interaction.channel
        user = ctx_or_interaction.user if is_slash else ctx_or_interaction.author

        match = re.search(self.TIKTOK_REGEX, target_message.content)
        if not match:
            msg = "🔍 No encontré un link de TikTok válido."
            return await ctx_or_interaction.followup.send(msg) if is_slash else await ctx_or_interaction.send(msg, delete_after=5)

        url = match.group(0)
        
        # Feedback visual con auto-eliminación en 15 segundos para limpieza
        status_msg = "⏳ **Procesando...**"
        if is_slash:
            status = await ctx_or_interaction.followup.send(status_msg, wait=True)
            await status.delete(delay=15)
        else:
            status = await ctx_or_interaction.send(status_msg)
            await status.delete(delay=15)

        file_name = f"tikt_{user.id}.mp4"
        file_path = os.path.join(self.cache_path, file_name)

        try:
            # Extracción de información (Título y Autor)
            ydl_opts_info = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video de TikTok')
                video_author = info.get('uploader', 'Desconocido')

            # Ejecución de descarga en hilo separado para no bloquear el bot
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.download_tiktok, url, file_path)

            if os.path.exists(file_path):
                # Mensaje minimalista: Título, Autor y URL
                content = (
                    f"🎬 **Título:** {video_title}\n"
                    f"👤 **Autor:** @{video_author}\n"
                    f"🔗 **URL:** <{url}>"
                )
                
                file = discord.File(file_path, filename="sybaru_video.mp4")
                
                # Enviamos el video (sin el botón de limpiar)
                await channel.send(content=content, file=file)
                
                # --- LIMPIEZA AUTOMÁTICA DEL CHAT ---
                try:
                    await target_message.delete() # Borra el mensaje con el link original
                    if not is_slash: 
                        await ctx_or_interaction.message.delete() # Borra el comando !tktk
                except: 
                    pass 
            else:
                await channel.send("❌ Error: No se pudo generar el archivo.", delete_after=10)
        except Exception as e:
            await channel.send(f"❌ Error técnico: `{str(e)[:50]}`", delete_after=10)
        finally:
            # Elimina el video del servidor para ahorrar espacio
            if os.path.exists(file_path):
                os.remove(file_path)

    @commands.command(name="tktk")
    async def tktk_prefix(self, ctx):
        """Comando con prefijo (!) mediante respuesta."""
        if not ctx.message.reference:
            return await ctx.send("❌ Responde a un TikTok para convertirlo.", delete_after=5)
        
        target = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await self.process_tikt(ctx, target)

    @app_commands.command(name="tktk", description="Convierte un TikTok respondiendo al mensaje")
    async def tktk_slash(self, interaction: discord.Interaction):
        """Comando Slash (/) mediante respuesta."""
        await interaction.response.defer(ephemeral=True)
        try:
            msg = await interaction.channel.fetch_message(interaction.message.id) if interaction.message else None
            if not msg or not msg.reference:
                return await interaction.followup.send("❌ Debes usar esto como respuesta.", ephemeral=True)
            
            target = await interaction.channel.fetch_message(msg.reference.message_id)
            await self.process_tikt(interaction, target)
        except:
            await interaction.followup.send("❌ Error de detección. Usa `!tktk`.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ConverTikt(bot))