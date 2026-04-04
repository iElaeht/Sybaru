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
        intents.voice_states = True     # Vital para FFmpeg
        intents.members = True          
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Carga recursiva de módulos y sincronización de comandos"""
        print("-" * 40)
        print("⚙️  Iniciando carga de módulos...")
        
        base_path = './src/commands'
        
        # Escaneamos carpetas y subcarpetas (incluyendo la de music)
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if filename.endswith('.py') and filename != '__init__.py':
                    relative_path = os.path.relpath(os.path.join(root, filename), '.')
                    module_path = relative_path.replace(os.sep, '.')[:-3]
                    
                    try:
                        await self.load_extension(module_path)
                        # Marcamos visualmente si es un módulo de música
                        icon = "🎵" if "music" in module_path else "✅"
                        print(f"{icon} Cargado: {module_path}")
                    except Exception as e:
                        print(f"❌ Error al cargar {module_path}: {e}")

        print("-" * 40)
        try:
            if GUILD_ID:
                # Sincronización rápida para tu servidor de pruebas
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"🔃 {len(synced)} Slash Commands sincronizados en Guild: {GUILD_ID}")
            else:
                synced = await self.tree.sync()
                print(f"🔃 {len(synced)} Slash Commands sincronizados globalmente.")
        except Exception as e:
            print(f"❌ Error en la sincronización: {e}")

    async def on_ready(self):
        print("-" * 40)
        print(f'🚀 {self.user.name} está online y operando con FFmpeg.')
        print(f'🆔 ID: {self.user.id}')
        print(f'📡 Prefijo: {DEFAULT_PREFIX}')
        print("-" * 40)

# 4. Función de ejecución
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
        print("\n👋 Sybaru se está apagando correctamente.")