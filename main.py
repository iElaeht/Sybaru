import discord
import os
import asyncio
import sys
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

from src.utils.database import init_db, get_guild_prefix

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '/')

def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX
    return get_guild_prefix(message.guild.id, DEFAULT_PREFIX)

class SybaruBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.members = True          
        intents.voice_states = True     
        intents.presences = True        
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,          
            case_insensitive=True       
        )

    async def setup_hook(self):
        print("-" * 40)
        print("📁 Inicializando Sistemas...")

        try:
            init_db()
            print("🗄️  Base de datos sincronizada correctamente.")
        except Exception as e:
            print(f"⚠️  Error crítico al iniciar la DB: {e}")

        print("-" * 40)
        print("⚙️  Cargando módulos de comandos...")
        
        folders_to_load = [
            os.path.join('src', 'commands'),
            os.path.join('src', 'utils_cmd') 
        ]
        
        for base_path in folders_to_load:
            if not os.path.exists(base_path):
                print(f"⚠️  Aviso: No se encontró la carpeta {base_path}")
                continue
                
            for root, _, files in os.walk(base_path):
                for filename in files:
                    if filename.endswith('.py') and not filename.startswith('__'):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, '.')
                        module_path = relative_path.replace(os.sep, '.')[:-3]
                        
                        try:
                            await self.load_extension(module_path)
                            icon = "🎵" if "music" in module_path else "🛠️" if "utils" in module_path else "✅"
                            print(f"{icon} Cargado: {module_path}")
                        except Exception as e:
                            print(f"❌ Error al cargar {module_path}: {e}")

        print("-" * 40)

        try:
            synced = await self.tree.sync()
            print(f"🔃 {len(synced)} Slash Commands sincronizados globalmente.")
        except Exception as e:
            print(f"❌ Error de sincronización de Slash Commands: {e}")

    async def on_ready(self):
        """Evento que se dispara cuando el bot está listo y conectado."""
        print("-" * 40)
        print(f'🚀 {self.user.name} está ONLINE y operando')
        print(f'🆔 ID: {self.user.id}')
        print(f'📡 Prefijo global: {DEFAULT_PREFIX}')
        print("-" * 40)
        status_text = f"{DEFAULT_PREFIX}comandos o /comandos | Sybaru"
        await self.change_presence(
            activity=discord.CustomActivity(name=status_text)
        )

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
        print("\n👋 Sybaru ha sido apagado manualmente.")
    except Exception as e:
        print(f"⚠️ Error inesperado en la ejecución: {e}")