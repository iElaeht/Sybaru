import discord
import os
import asyncio
import sys
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
        print("SISTEMA: Inicializando procesos...")

        try:
            init_db()
            print("DB: Sincronizacion completada.")
        except Exception as e:
            print(f"DB_ERROR: Fallo critico en inicio de base de datos: {e}")

        folders_to_load = [
            os.path.join('src', 'commands'),
            os.path.join('src', 'utils_cmd') 
        ]
        
        for base_path in folders_to_load:
            if not os.path.exists(base_path):
                print(f"SISTEMA_AVISO: Directorio no encontrado: {base_path}")
                continue
                
            for root, _, files in os.walk(base_path):
                for filename in files:
                    if filename.endswith('.py') and not filename.startswith('__'):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, '.')
                        module_path = relative_path.replace(os.sep, '.')[:-3]
                        
                        try:
                            await self.load_extension(module_path)
                            print(f"MODULO: Cargado {module_path}")
                        except Exception as e:
                            print(f"MODULO_ERROR: Fallo al cargar {module_path}: {e}")

        try:
            synced = await self.tree.sync()
            print(f"SYNC: {len(synced)} Slash Commands sincronizados.")
        except Exception as e:
            print(f"SYNC_ERROR: Fallo en sincronizacion global: {e}")

    async def on_ready(self):
        print(f"STATUS: {self.user.name} online.")
        print(f"ID: {self.user.id}")
        
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
            print("AUTH_ERROR: TOKEN no definido en .env")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("SISTEMA: Apagado manual detectado.")
    except Exception as e:
        print(f"SISTEMA_ERROR: Excepcion en ejecucion: {e}")