import discord
import os
import asyncio
import json
import sys
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# --- CORRECCIÓN CRÍTICA PARA WINDOWS ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ---------------------------------------

# 1. Cargar las variables de entorno
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '!')
GUILD_ID = os.getenv('SERVER_ID') 

# 2. Gestión de prefijos por servidor
def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX
    try:
        if os.path.exists('prefixes.json'):
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            return prefixes.get(str(message.guild.id), DEFAULT_PREFIX)
        return DEFAULT_PREFIX
    except Exception:
        return DEFAULT_PREFIX

# 3. Clase principal del Bot Sybaru
class SybaruBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.voice_states = True     # Vital para FFmpeg y Música
        intents.members = True          
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Carga recursiva de módulos y sincronización de comandos"""
        
        # --- INICIALIZACIÓN DE DB ---
        try:
            from src.utils.database import init_db
            init_db()
            print("🗄️  Base de datos preparada.")
        except Exception as e:
            print(f"⚠️  Advertencia al iniciar DB: {e}")

        print("-" * 40)
        print("⚙️  Iniciando carga de módulos...")
        
        # Ruta base donde están los comandos
        base_path = os.path.join('.', 'src', 'commands')
        
        # Escaneamos carpetas y subcarpetas
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if filename.endswith('.py') and filename != '__init__.py':
                    # Convertimos la ruta del archivo en un path de módulo (ej: src.commands.music.play)
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, '.')
                    module_path = relative_path.replace(os.sep, '.')[:-3]
                    
                    try:
                        await self.load_extension(module_path)
                        icon = "🎵" if "music" in module_path else "✅"
                        print(f"{icon} Cargado: {module_path}")
                    except Exception as e:
                        print(f"❌ Error al cargar {module_path}: {e}")

        print("-" * 40)

# --- SINCRONIZACIÓN DE SLASH COMMANDS ---
        try:
            # Forzamos sincronización global para que limpie errores previos
            synced = await self.tree.sync()
            print(f"🔃 {len(synced)} Slash Commands sincronizados globalmente.")
        except Exception as e:
            print(f"❌ Error en la sincronización: {e}")

    async def on_ready(self):
        print("-" * 40)
        print(f'🚀 {self.user.name} está online y operando con FFmpeg.')
        print(f'🆔 ID: {self.user.id}')
        print(f'📡 Prefijo por defecto: {DEFAULT_PREFIX}')
        print("-" * 40)
        
        # Estado del bot
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=f"{DEFAULT_PREFIX}comandos | Sybaru"
        ))

# 4. Función de ejecución principal
async def run_bot():
    bot = SybaruBot()
    async with bot:
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("❌ ERROR: No se encontró el TOKEN en el archivo .env")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Sybaru se está apagando correctamente. ¡Hasta pronto!")
    except Exception as e:
        print(f"⚠️ Error inesperado al iniciar: {e}")