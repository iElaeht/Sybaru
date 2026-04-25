import discord
from discord.ext import commands
from discord import app_commands
import difflib
from src.utils.database import add_crosshair, get_crosshairs, update_crosshair, delete_crosshair

# --- CLASE PARA LA PAGINACIÓN ---
class CrosshairPagination(discord.ui.View):
    def __init__(self, miras, user_name):
        super().__init__(timeout=60)
        self.miras = miras
        self.user_name = user_name
        self.current_page = 0
        self.per_page = 5 

    def create_embed(self):
        total_pages = (len(self.miras) - 1) // self.per_page + 1
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_miras = self.miras[start:end]
        
        embed = discord.Embed(
            title="🎯 Mi Colección de Crosshairs",
            description="> *Copia e importa estos códigos en los ajustes de Valorant.*",
            color=discord.Color.from_rgb(255, 70, 85) # Rojo Valorant
        )
        
        embed.set_author(name=f"Sybaru Armory: {self.user_name}", icon_url="https://i.imgur.com/8Q9Z5R1.png")
        
        for title, code in page_miras:
            embed.add_field(name=f"📌 {title}", value=f"```text\n{code}\n```", inline=False)
        
        embed.set_footer(text=f"Página {self.current_page + 1} de {total_pages}  •  Total: {len(self.miras)} miras")
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.current_page + 1) * self.per_page < len(self.miras):
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

# --- CLASE PRINCIPAL ---
class Crosshair(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_suggestion(self, target, miras):
        nombres = [m[0] for m in miras]
        matches = difflib.get_close_matches(target, nombres, n=1, cutoff=0.6)
        return matches[0] if matches else None

    chr_group = app_commands.Group(name="chr", description="Gestión inteligente de miras")

    @chr_group.command(name="agregar", description="Guarda una nueva mira")
    async def agregar(self, interaction: discord.Interaction, titulo: str, codigo: str):
        if add_crosshair(interaction.user.id, titulo, codigo):
            await interaction.response.send_message(f"✅ Mira **{titulo}** guardada correctamente.", ephemeral=True, delete_after=15)
        else:
            await interaction.response.send_message(f"⚠️ La mira **{titulo}** ya existe. Usa `/chr editar`.", ephemeral=True, delete_after=15)

    @chr_group.command(name="lista", description="Muestra tus miras con privacidad dinámica")
    @app_commands.describe(mostrar="¿Quieres que la lista sea pública o privada?")
    @app_commands.choices(mostrar=[
        app_commands.Choice(name="Privado 🔒 (Solo yo lo veo)", value="si"),
        app_commands.Choice(name="Público 🌍 (Mostrar a todos)", value="no")
    ])
    async def lista(self, interaction: discord.Interaction, mostrar: app_commands.Choice[str]):
        miras = get_crosshairs(interaction.user.id)
        if not miras:
            return await interaction.response.send_message("❌ Tu armería está vacía.", ephemeral=True)

        es_privado = (mostrar.value == "si")
        view = CrosshairPagination(miras, interaction.user.display_name)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=es_privado)

    @chr_group.command(name="editar", description="Actualiza una mira existente")
    async def editar(self, interaction: discord.Interaction, titulo: str, nuevo_codigo: str):
        if update_crosshair(interaction.user.id, titulo, nuevo_codigo):
            await interaction.response.send_message(f"📝 Mira **{titulo}** actualizada.", ephemeral=True, delete_after=15)
        else:
            miras = get_crosshairs(interaction.user.id)
            sugerencia = self.get_suggestion(titulo, miras)
            msg = f"❌ No encontré la mira **{titulo}**."
            if sugerencia: msg += f" ¿Quisiste decir **{sugerencia}**?"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

    @chr_group.command(name="eliminar", description="Borra una mira")
    async def eliminar(self, interaction: discord.Interaction, titulo: str):
        if delete_crosshair(interaction.user.id, titulo):
            await interaction.response.send_message(f"🗑️ Mira **{titulo}** eliminada.", ephemeral=True, delete_after=15)
        else:
            miras = get_crosshairs(interaction.user.id)
            sugerencia = self.get_suggestion(titulo, miras)
            msg = f"❌ No se pudo eliminar **{titulo}**."
            if sugerencia: msg += f" ¿Quizás es **{sugerencia}**?"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

    @chr_group.command(name="buscar", description="Busca una mira específica")
    @app_commands.describe(mostrar="¿Quieres mostrar el resultado al canal?")
    @app_commands.choices(mostrar=[
        app_commands.Choice(name="Privado 🔒", value="si"),
        app_commands.Choice(name="Público 🌍", value="no")
    ])
    async def buscar(self, interaction: discord.Interaction, titulo: str, mostrar: app_commands.Choice[str]):
        miras = get_crosshairs(interaction.user.id)
        mira = next((m for m in miras if m[0].lower() == titulo.lower()), None)
        
        es_privado = (mostrar.value == "si")

        if mira:
            embed = discord.Embed(
                title=f"🔍 Resultado: {mira[0]}",
                description="> Código listo para copiar e importar.",
                color=discord.Color.from_rgb(255, 70, 85)
            )
            embed.add_field(name="Código", value=f"```text\n{mira[1]}\n```")
            await interaction.response.send_message(embed=embed, ephemeral=es_privado)
        else:
            sugerencia = self.get_suggestion(titulo, miras)
            msg = f"🔍 No encontré **{titulo}**."
            if sugerencia: msg += f" ¿Quisiste decir **{sugerencia}**?"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

async def setup(bot):
    await bot.add_cog(Crosshair(bot))