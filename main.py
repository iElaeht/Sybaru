import discord
import os
import asyncio
import sys
import threading
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# --- CONFIGURACIÓN DE FASTAPI (Para mantener vivo en Render) ---
app = FastAPI()

@app.get("/")
def read_root():
    # Render visitará esta ruta cada pocos minutos
    return {"status": "Sybaru Bot Operacional", "port": os.getenv("PORT", "10000")}

def run_api():
    # Render asigna el puerto dinámicamente, por defecto 10000
    port = int(os.getenv("PORT", 10000))
    print(f"SISTEMA: API de vida iniciada en el puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

# --- LÓGICA DEL BOT ---

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '/')

# Importación segura de la base de datos
try:
    from src.utils.database import init_db, get_guild_prefix
except ImportError:
    print("SISTEMA_ERROR: No se encontró 'src.utils.database'.")

def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX
    try:
        return get_guild_prefix(message.guild.id, DEFAULT_PREFIX)
    except:
        return DEFAULT_PREFIX

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

        # --- PARCHE DE COOKIES PARA YOUTUBE ---
        # Esto soluciona que el bot entre y se salga del VC
        cookies = os.getenv("youtube_cookies")
        if cookies:
            try:
                with open("youtube_cookies.txt", "w", encoding="utf-8") as f:
                    f.write(cookies)
                print("SISTEMA: Archivo youtube_cookies.txt generado.")
            except Exception as e:
                print(f"SISTEMA_ERROR: Fallo al crear archivo de cookies: {e}")

        # --- INICIO DE BASE DE DATOS ---
        try:
            init_db()
            print("DB: Sincronizacion completada.")
        except Exception as e:
            print(f"DB_ERROR: Fallo en base de datos: {e}")

        # --- CARGA DE COMANDOS ---
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

        # --- SINCRONIZACIÓN DE SLASH COMMANDS ---
        try:
            synced = await self.tree.sync()
            print(f"SYNC: {len(synced)} Slash Commands sincronizados.")
        except Exception as e:
            print(f"SYNC_ERROR: Fallo en sincronizacion: {e}")

    async def on_ready(self):
        print(f"STATUS: {self.user.name} online en Render 24/7.")
        print(f"ID: {self.user.id}")
        
        status_text = f"{DEFAULT_PREFIX}comandos | Sybaru"
        await self.change_presence(
            activity=discord.CustomActivity(name=status_text)
        )

async def run_bot():
    # 1. Iniciamos FastAPI en un hilo aparte para no bloquear al bot
    threading.Thread(target=run_api, daemon=True).start()
    
    # 2. Iniciamos el bot
    bot = SybaruBot()
    async with bot:
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("AUTH_ERROR: TOKEN no definido en las variables de Render.")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("SISTEMA: Apagado manual.")
    except Exception as e:
        print(f"SISTEMA_ERROR: Excepcion en ejecucion: {e}")