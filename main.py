import discord
import os
import asyncio
import json
import sys
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# --- CORRECCIÓN PARA WINDOWS ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 1. Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '!')

# 2. Gestión de prefijos
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

# 3. Clase principal
class SybaruBot(commands.Bot):
    def __init__(self):
        # Aseguramos los intents necesarios para música e información de servidor
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.voice_states = True     # Vital para Música
        intents.members = True          # Necesario para el comando InfoServer
        intents.presences = True        # Opcional, pero útil para info detallada
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Carga de base de datos y módulos (Comandos y Utils)"""
        
        # --- INICIALIZACIÓN DE DB ---
        try:
            from src.utils.database import init_db
            init_db()
            print("🗄️  Base de datos preparada.")
        except Exception as e:
            print(f"⚠️  Advertencia al iniciar DB: {e}")

        print("-" * 40)
        print("⚙️  Iniciando carga de módulos...")
        
        # Definimos las carpetas que queremos escanear para cargar Cogs
        # He añadido 'src/utils_cmd' para que cargue tu nuevo infoserver.py automáticamente
        folders_to_load = [
            os.path.join('.', 'src', 'commands'),
            os.path.join('.', 'src', 'utils_cmd') 
        ]
        
        for base_path in folders_to_load:
            if not os.path.exists(base_path):
                continue
                
            for root, dirs, files in os.walk(base_path):
                for filename in files:
                    if filename.endswith('.py') and filename != '__init__.py':
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, '.')
                        module_path = relative_path.replace(os.sep, '.')[:-3]
                        
                        try:
                            await self.load_extension(module_path)
                            # Iconos personalizados según el tipo de módulo
                            icon = "🎵" if "music" in module_path else "🛠️" if "utils" in module_path else "✅"
                            print(f"{icon} Cargado: {module_path}")
                        except Exception as e:
                            print(f"❌ Error al cargar {module_path}: {e}")

        print("-" * 40)

        # --- SINCRONIZACIÓN ---
        try:
            synced = await self.tree.sync()
            print(f"🔃 {len(synced)} Slash Commands sincronizados globalmente.")
        except Exception as e:
            print(f"❌ Error en la sincronización: {e}")

    async def on_ready(self):
        print("-" * 40)
        print(f'🚀 {self.user.name} está online.')
        print(f'🆔 ID: {self.user.id}')
        print(f'📡 Prefijo: {DEFAULT_PREFIX}')
        print("-" * 40)
        
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=f"{DEFAULT_PREFIX}comandos | Sybaru"
        ))

# 4. Ejecución
async def run_bot():
    bot = SybaruBot()
    async with bot:
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("❌ ERROR: No hay TOKEN.")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Sybaru apagado.")
    except Exception as e:
        print(f"⚠️ Error: {e}")