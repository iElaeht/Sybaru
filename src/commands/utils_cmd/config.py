import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class Config(commands.Cog):
    """
    Cog de configuración de Sybaru utilizando persistencia SQL.
    Gestiona el prefijo de forma eficiente y segura.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'sybaru_config.db'
        self._init_db()

    def _init_db(self):
        """Inicializa la tabla de prefijos si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id TEXT PRIMARY KEY,
                    prefix TEXT
                )
            ''')
            conn.commit()

    def _set_guild_prefix(self, guild_id, prefix):
        """Inserta o actualiza el prefijo de un servidor en la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prefixes (guild_id, prefix) 
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET prefix = excluded.prefix
            ''', (str(guild_id), prefix))
            conn.commit()

    @commands.hybrid_command(
        name="setprefix", 
        description="Cambia el prefijo de Sybaru para este servidor."
    )
    @app_commands.describe(nuevo_prefijo="El nuevo símbolo (ej: $, ., !)")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, nuevo_prefijo: str):
        """
        Cambia el prefijo y lo guarda en la base de datos SQLite.
        """
        # Validación de seguridad
        if len(nuevo_prefijo) > 5:
            return await ctx.send("❌ El prefijo es demasiado largo (máximo 5 caracteres).", ephemeral=True)

        # Guardar en base de datos
        try:
            self._set_guild_prefix(ctx.guild.id, nuevo_prefijo)
            
            embed = discord.Embed(
                title="⚙️ Configuración Guardada",
                description=f"El nuevo prefijo para este servidor es: `{nuevo_prefijo}`",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Cambio aplicado por {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Error al guardar en DB: {e}")
            await ctx.send("❌ Hubo un problema técnico al guardar la configuración.")

async def setup(bot):
    """Carga del módulo de configuración con soporte SQL."""
    await bot.add_cog(Config(bot))