import discord
import os
import asyncio
import sys
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

# Importamos las funciones centrales de tu base de datos
from src.utils.database import init_db, get_guild_prefix

# --- CONFIGURACIÓN DE ENTORNO ---
# Solución de compatibilidad para evitar errores de cierre en Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '!')

# --- GESTIÓN DE PREFIJOS DINÁMICOS ---
def get_prefix(bot, message):
    """
    Consulta el prefijo en la DB delegando la lógica al módulo de base de datos.
    Si es un mensaje privado (MD) o no hay registro, usa el predeterminado.
    """
    if not message.guild:
        return DEFAULT_PREFIX
    
    # Llamamos a la función de src/utils/database.py
    return get_guild_prefix(message.guild.id, DEFAULT_PREFIX)

# --- CLASE PRINCIPAL DEL BOT ---
class SybaruBot(commands.Bot):
    def __init__(self):
        # Configuración de facultades (Intents)
        intents = discord.Intents.default()
        intents.message_content = True  # Leer comandos de texto
        intents.members = True          # Información de usuarios (ServerInfo/UserInfo)
        intents.voice_states = True     # Vital para el motor de música
        intents.presences = True        # Ver estados (Online/Offline)
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,          # Deshabilitado para usar uno personalizado
            case_insensitive=True       # !Comando y !comando funcionarán igual
        )

    async def setup_hook(self):
        """Inicialización de sistemas, DB y carga automática de módulos."""
        print("-" * 40)
        print("📁 Inicializando Sistemas...")

        # 1. Sincronizar Base de Datos (Crea tablas si no existen)
        try:
            init_db()
            print("🗄️  Base de datos sincronizada correctamente.")
        except Exception as e:
            print(f"⚠️  Error crítico al iniciar la DB: {e}")

        print("-" * 40)
        print("⚙️  Cargando módulos de comandos...")
        
        # 2. Carga automática de Cogs (Carpetas commands y utils_cmd)
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
                    # Cargamos solo archivos .py y omitimos los __init__.py
                    if filename.endswith('.py') and not filename.startswith('__'):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, '.')
                        # Convertimos ruta de archivo a formato de módulo Python (ej: src.commands.music)
                        module_path = relative_path.replace(os.sep, '.')[:-3]
                        
                        try:
                            await self.load_extension(module_path)
                            # Emoji decorativo según el tipo de módulo
                            icon = "🎵" if "music" in module_path else "🛠️" if "utils" in module_path else "✅"
                            print(f"{icon} Cargado: {module_path}")
                        except Exception as e:
                            print(f"❌ Error al cargar {module_path}: {e}")

        print("-" * 40)

        # 3. Sincronización de Slash Commands (Comandos de barra '/')
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
        
        # Actividad visual en el perfil del bot
        status_text = f"{DEFAULT_PREFIX}ayuda | Sybaru"
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=status_text
        ))

# --- FUNCIÓN DE ARRANQUE ---
async def run_bot():
    bot = SybaruBot()
    async with bot:
        if TOKEN:
            await bot.start(TOKEN)
        else:
            print("❌ ERROR: No se encontró el TOKEN en el archivo .env")

# Punto de entrada del script
if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Sybaru ha sido apagado manualmente.")
    except Exception as e:
        print(f"⚠️ Error inesperado en la ejecución: {e}")