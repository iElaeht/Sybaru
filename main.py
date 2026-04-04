import discord
import os
import asyncio
import json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# 1. Cargar las variables de entorno
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '!')
GUILD_ID = os.getenv('SERVER_ID') 


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

# 3. Clase principal del Bot
class SybaruBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Carga de módulos y sincronización de comandos"""
        print("-" * 30)
        print("⚙️  Cargando módulos de comandos...")
        
        commands_path = './src/commands'
        
        # Cargar los archivos .py de la carpeta commands
        if os.path.exists(commands_path):
            for filename in os.listdir(commands_path):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'src.commands.{filename[:-3]}')
                        print(f"✅ Módulo cargado: {filename}")
                    except Exception as e:
                        print(f"❌ Error al cargar {filename}: {e}")

        # Sincronización de Slash Commands
        try:
            if GUILD_ID:
                # Sincronización Local (Instantánea para tu servidor de pruebas)
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"🔃 Sincronizados {len(synced)} comandos localmente en el servidor: {GUILD_ID}")
            else:
                # Sincronización Global (Puede tardar hasta 1 hora en actualizarse)
                synced = await self.tree.sync()
                print(f"🔃 Sincronizados {len(synced)} comandos globales.")
        except Exception as e:
            print(f"❌ Error en la sincronización: {e}")

    async def on_ready(self):
        print("-" * 30)
        print(f'🚀 {self.user.name} está en línea y operando.')
        print(f'🆔 ID: {self.user.id}')
        print(f'📡 Prefijo base: {DEFAULT_PREFIX}')
        print("-" * 30)

# 4. Función de arranque
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
        print("\n👋 Sybaru se está apagando... ¡Hasta pronto!")