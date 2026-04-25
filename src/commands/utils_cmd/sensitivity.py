import discord
from discord.ext import commands
from discord import app_commands
import difflib
# Importamos las funciones de nuestra base de datos (que luego actualizaremos)
from src.utils.database import add_sensitivity, get_sensitivities, update_sensitivity, delete_sensitivity

class SensPagination(discord.ui.View):
    def __init__(self, data, user_name):
        super().__init__(timeout=60)
        self.data = data
        self.user_name = user_name
        self.current_page = 0
        self.per_page = 5

    def create_embed(self):
        total_pages = (len(self.data) - 1) // self.per_page + 1
        start = self.current_page * self.per_page
        page_items = self.data[start:start + self.per_page]
        
        embed = discord.Embed(
            title="🖱️ Mis Sensibilidades Tácticas",
            description="> *Configuraciones detalladas de DPI, Sens y Multiplicadores.*",
            color=discord.Color.from_rgb(0, 255, 127)
        )
        embed.set_author(name=f"Sybaru Armory: {self.user_name}", icon_url="https://i.imgur.com/8Q9Z5R1.png")

        for title, dpi, sens, scoped, ads in page_items:
            # Calculamos el eDPI (DPI * Sens) solo como referencia visual si son números
            try:
                edpi = float(dpi) * float(sens)
                footer_val = f"**eDPI:** `{edpi:.2f}`"
            except:
                footer_val = ""

            embed.add_field(
                name=f"🎮 {title}", 
                value=(
                    f"**DPI:** `{dpi}` | **Sens:** `{sens}`\n"
                    f"**Scoped:** `{scoped}` | **ADS:** `{ads}`\n"
                    f"{footer_val}"
                ), 
                inline=False
            )
        
        embed.set_footer(text=f"Página {self.current_page + 1} de {total_pages} • Total: {len(self.data)}")
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.current_page + 1) * self.per_page < len(self.data):
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

class Sensitivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_suggestion(self, target, data):
        titles = [item[0] for item in data]
        matches = difflib.get_close_matches(target, titles, n=1, cutoff=0.6)
        return matches[0] if matches else None

    sens_group = app_commands.Group(name="sens", description="Gestión táctica de sensibilidades")

    @sens_group.command(name="agregar", description="Guarda una configuración completa (DPI, Sens, Scoped, ADS)")
    @app_commands.describe(
        titulo="Nombre del perfil (ej: Valorant Main)",
        dpi="Tu DPI actual (ej: 800)",
        sens="Sensibilidad de mira (ej: 0.21)",
        scoped="Multiplicador de mira de francotirador (ej: 1.0)",
        ads="Multiplicador de mira ADS (ej: 1.0)"
    )
    async def agregar(self, interaction: discord.Interaction, titulo: str, dpi: str, sens: str, scoped: str = "1.0", ads: str = "1.0"):
        # Llamamos a la DB con los nuevos parámetros
        if add_sensitivity(interaction.user.id, titulo, dpi, sens, scoped, ads):
            await interaction.response.send_message(f"✅ Configuración **{titulo}** guardada con éxito.", ephemeral=True, delete_after=15)
        else:
            await interaction.response.send_message(f"⚠️ **{titulo}** ya existe. Usa `/sens editar`.", ephemeral=True, delete_after=15)

    @sens_group.command(name="listar", description="Muestra tus sensibilidades")
    @app_commands.describe(mostrar="¿Privado o Público?")
    @app_commands.choices(mostrar=[
        app_commands.Choice(name="Privado 🔒", value="si"),
        app_commands.Choice(name="Público 🌍", value="no")
    ])
    async def listar(self, interaction: discord.Interaction, mostrar: app_commands.Choice[str]):
        data = get_sensitivities(interaction.user.id)
        if not data:
            return await interaction.response.send_message("❌ No tienes sensibilidades guardadas.", ephemeral=True)
        
        es_privado = (mostrar.value == "si")
        view = SensPagination(data, interaction.user.display_name)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=es_privado)

    @sens_group.command(name="editar", description="Actualiza todos los valores de una sensibilidad")
    async def editar(self, interaction: discord.Interaction, titulo: str, nuevo_dpi: str, nueva_sens: str, nuevo_scoped: str, nueva_ads: str):
        if update_sensitivity(interaction.user.id, titulo, nuevo_dpi, nueva_sens, nuevo_scoped, nueva_ads):
            await interaction.response.send_message(f"📝 **{titulo}** actualizada correctamente.", ephemeral=True, delete_after=15)
        else:
            data = get_sensitivities(interaction.user.id)
            sug = self.get_suggestion(titulo, data)
            msg = f"❌ No existe **{titulo}**."
            if sug: msg += f" ¿Quisiste decir **{sug}**?"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

    @sens_group.command(name="eliminar", description="Borra una configuración")
    async def eliminar(self, interaction: discord.Interaction, titulo: str):
        if delete_sensitivity(interaction.user.id, titulo):
            await interaction.response.send_message(f"🗑️ **{titulo}** eliminada.", ephemeral=True, delete_after=15)
        else:
            data = get_sensitivities(interaction.user.id)
            sug = self.get_suggestion(titulo, data)
            msg = f"❌ No se pudo eliminar **{titulo}**."
            if sug: msg += f" ¿Quizás es **{sug}**?"
            await interaction.response.send_message(msg, ephemeral=True, delete_after=15)

async def setup(bot):
    await bot.add_cog(Sensitivity(bot))